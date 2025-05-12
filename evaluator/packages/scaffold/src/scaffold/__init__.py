import json
import os
import shutil
import subprocess
import structlog

from .log_to_html import generate_log_html

from .pages.index_html import index_html

from .config import get_config
from agent.datatypes import TestParameters, TestToRun, ResultStats


LOG = structlog.get_logger(__name__)


def create_site(output_file: str, tests: list[TestToRun]):
    html = index_html(output_file, tests)
    with open(output_file, "w") as f:
        f.write(str(html))


def run_test(
    test: TestToRun,
):
    LOG.info(
        "starting_test",
        provider=test.provider.name,
        model=test.model,
        test_folder=test.input_folder,
    )

    LOG.info(
        "setting_up_environment",
        provider=test.provider.name,
        model=test.model,
    )
    # Set up environment
    os.makedirs(test.output_folder, exist_ok=True)
    shutil.copytree(
        os.path.join(test.input_folder),
        os.path.join(test.output_folder),
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("config.json"),
    )

    # Spin up docker container
    name = f"{test.name}_{test.provider.name}_{test.model}"
    docker_name = "".join([c for c in name if c.isalnum() or c in "_-"])
    agent_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "agent")
    )
    LOG.info(
        f"start_container", name={docker_name}, image=test.test_parameters.docker_image
    )

    # We're reapping paths when we go into docker
    local_test_config = TestToRun(
        name=test.name,
        test_parameters=test.test_parameters,
        provider=test.provider,
        model=test.model,
        input_folder="/project",
        output_folder="/project",
    )
    res = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{test.output_folder}:/project",
            "-v",
            f"{agent_folder}:/agent",
            "-w",
            "/agent",
            "-e",
            f"TEST_CONFIG={local_test_config.model_dump_json()}",
            "--name",
            docker_name,
            test.test_parameters.docker_image,
            "/bin/bash",
            "-c",
            f"/agent/run.sh",
        ]
    )
    if res.returncode != 0:
        raise RuntimeError(f"Agent Failed to Run: {res.stderr}")

    # copy the config.py file to the output folder so we can compare config between runs
    shutil.copy(
        os.path.join(test.input_folder, "config.json"),
        os.path.join(test.output_folder, "config.json"),
    )


def generate_html_log_file(test: TestToRun):
    stats = open(os.path.join(test.output_folder, "stats.json"), "r")
    stats = ResultStats.model_validate_json(stats.read())

    log = stats.log
    log_html = generate_log_html(log)
    with open(os.path.join(test.output_folder, "log.html"), "w") as f:
        f.write(log_html)


def main():
    config = get_config()
    providers = config.providers
    test_folders = os.listdir(config.test_input_directory)

    tests_to_run: list[TestToRun] = []
    test_names: list[str] = []
    for test_folder in test_folders:
        test_settings_file = os.path.join(
            config.test_input_directory, test_folder, "config.json"
        )
        test_parameters = TestParameters.model_validate(
            json.load(open(test_settings_file, "r"))
        )
        assert test_parameters.name not in test_names, (
            f"Duplicate test name: {test_parameters.name}"
        )
        test_names.append(test_parameters.name)

        for provider in providers:
            for model in provider.models:
                output_folder = os.path.join(
                    os.path.abspath(config.test_output_directory),
                    provider.name,
                    model,
                    test_folder,
                )

                tests_to_run.append(
                    TestToRun(
                        name=test_folder,
                        test_parameters=test_parameters,
                        provider=provider,
                        model=model,
                        input_folder=os.path.join(
                            config.test_input_directory, test_folder
                        ),
                        output_folder=output_folder,
                    )
                )

    # Sort by provider name and model name
    tests_to_run.sort(key=lambda x: (x.provider.name, x.model))

    create_site(os.path.join(config.test_output_directory, "index.html"), tests_to_run)

    for test in tests_to_run:
        existing_config_file = os.path.join(test.output_folder, "config.json")
        if os.path.exists(existing_config_file):
            with open(existing_config_file, "r") as f:
                existing_config = f.read()
            with open(os.path.join(test.input_folder, "config.json"), "r") as f:
                new_config = f.read()

            if existing_config == new_config:
                LOG.info(
                    "skipping_test",
                    provider=test.provider.name,
                    model=test.model,
                    test_folder=test.input_folder,
                    output_folder=test.output_folder,
                )
                continue
        try:
            run_test(test)
        except Exception as _e:
            LOG.exception(
                "test_failed",
                provider=test.provider.name,
                model=test.model,
                test_folder=test.input_folder,
            )
            continue

        generate_html_log_file(test)


def run():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    main()


if __name__ == "__main__":
    run()
