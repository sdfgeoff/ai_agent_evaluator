import json
import os
import shutil
import subprocess
import structlog

from .config import get_config
from agent.agent.datatypes import TestParameters, TestToRun


LOG = structlog.get_logger(__name__)


def run_test(
    output_folder: str,
    test: TestToRun,
):
    LOG.info(
        "starting_test",
        provider=test.provider.name,
        model=test.model,
        test_folder=test.test_folder,
    )

    LOG.info(
        "setting_up_environment",
        provider=test.provider.name,
        model=test.model,
    )
    # Set up environment
    os.makedirs(output_folder, exist_ok=True)
    shutil.copytree(
        os.path.join(test.test_folder),
        os.path.join(output_folder),
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("config.json"),
    )

    # Spin up docker container
    name=f"{test.name}_{test.provider.name}_{test.model}"
    docker_name = "".join([c for c in name if c.isalnum() or c in "_-"])
    agent_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agent"))
    LOG.info(f"start_container", name={docker_name}, image=test.test_parameters.docker_image)
    
    # We're reapping paths when we go into docker
    local_test_config = TestToRun(
        name=test.name,
        test_parameters=test.test_parameters,
        provider=test.provider,
        model=test.model,
        test_folder="/project",  
    )
    res = subprocess.run([
        "docker",
        "run",
        "--rm",
        "-v", f"{output_folder}:/project",
        "-v", f"{agent_folder}:/agent:ro",
        "-w", "/agent",
        '-e', f"TEST_CONFIG={local_test_config.model_dump_json()}",
        "--name", docker_name,
        test.test_parameters.docker_image,
        "/bin/bash", "-c", f'/agent/run.sh',
        
    ])
    if res.returncode != 0:
        raise RuntimeError(f"Agent Failed to Run: {res.stderr}")


def main():
    config = get_config()
    providers = config.providers
    test_folders = os.listdir(config.test_input_directory)

    tests_to_run: list[TestToRun] = []
    for test_folder in test_folders:
        test_settings_file = os.path.join(
            config.test_input_directory, test_folder, "config.json"
        )
        test_parameters = TestParameters.model_validate(
            json.load(open(test_settings_file, "r"))
        )
        for provider in providers:
            for model in provider.models:
                tests_to_run.append(
                    TestToRun(
                        name=test_folder,
                        test_parameters=test_parameters,
                        provider=provider,
                        model=model,
                        test_folder=os.path.join(
                            config.test_input_directory, test_folder
                        ),
                    )
                )

    # Sort by provider name and model name
    tests_to_run.sort(key=lambda x: (x.provider.name, x.model))

    for test in tests_to_run:
        output_folder = os.path.join(
            os.path.abspath(config.test_output_directory),
            test.provider.name,
            test.model,
            test.name,
        )

        if os.path.exists(output_folder):
            LOG.info(
                "skipping_test",
                provider=test.provider.name,
                model=test.model,
                test_folder=test.test_folder,
            )
            continue

        try:
            run_test(output_folder, test)
        except Exception as e:
            LOG.exception(
                "test_failed",
                provider=test.provider.name,
                model=test.model,
                test_folder=test.test_folder,
            )
            continue


if __name__ == "__main__":
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
