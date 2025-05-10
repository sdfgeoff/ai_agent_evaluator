from collections import defaultdict
import json
import os
import shutil
import subprocess
import structlog

from .html import Tag

from .config import get_config
from agent.agent.datatypes import TestParameters, TestToRun


LOG = structlog.get_logger(__name__)


def create_index(output_file: str, tests_to_run: list[TestToRun]):

    by_model: dict[str, list[TestToRun]] = defaultdict(list)
    for test in tests_to_run:
        model = test.provider.name + "_" + test.model
        if model not in by_model:
            by_model[model].append(test)

    by_test_name: dict[str, list[TestToRun]] = defaultdict(list)
    for test in tests_to_run:
        test_name = test.test_parameters.name
        by_test_name[test_name].append(test)

    with Tag("html") as html:
        with Tag("head", html) as head:
            with Tag("title", head) as title:
                title.add("Evaluation Results")
            with Tag("style", head) as style:
                style.add(
                    """
                    body {
                        font-family: Arial, sans-serif;
                        margin: 20px;
                        padding: 20px;
                        background-color: #f4f4f4;
                    }
                    h1 {
                        color: #333;
                    }
                    .zoom-outer {
                        width: 480px;
                        height: 270px;
                        background-color: #fff;
                    }
                    .zoom-inner {
                        transform: scale(0.25);
                        transform-origin: 0 0;
                    }

                    .run_card {
                        background-color: #ddd;
                        border-radius: 5px;   
                        padding: 10px;   
                    }

                    .run_container {
                        display: flex;
                        flex-wrap: wrap;
                        gap: 20px;
                    }

                    """
                )
        with Tag("body", html) as body:
            for test, tests in by_test_name.items():
                with Tag("div", body) as test_div:
                    with Tag("h1", test_div) as h1:
                        h1.add(test)
                    with Tag("p", test_div) as p:
                        p.add(tests[0].test_parameters.blurb)
                    with Tag("p", test_div) as p:
                        p.add("Initial Prompt: " + tests[0].test_parameters.initial_prompt)

                    with Tag("div", test_div, class_="run_container") as run_container:
                        for run in tests:
                            with Tag("div", run_container, class_="run_card") as run_div:
                                with Tag("h2", run_div) as h2:
                                    h2.add(f"{run.provider.name} - {run.model}")
                                # iframe of output_folder.index.html
                                with Tag("div", run_div, class_="zoom-outer") as zoom_div_outer:
                                    with Tag("div", zoom_div_outer, class_="zoom-inner") as zoom_div:
                                        with Tag("iframe", zoom_div, src=f"{run.output_folder}/index.html", width="1920", height="1080") as iframe: 
                                            pass    
                                with Tag("a", run_div, href=f"{run.output_folder}/index.html") as a:
                                    a.add("View Full Size")
                                run_div.add(" ")
                                with Tag("a", run_div, href=f"{run.output_folder}/log.html") as a:
                                    a.add("View Message Log")
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
        input_folder="/project",  
        output_folder="/project",
    )
    res = subprocess.run([
        "docker",
        "run",
        "--rm",
        "-v", f"{test.output_folder}:/project",
        "-v", f"{agent_folder}:/agent:ro",
        "-w", "/agent",
        '-e', f"TEST_CONFIG={local_test_config.model_dump_json()}",
        "--name", docker_name,
        test.test_parameters.docker_image,
        "/bin/bash", "-c", f'/agent/run.sh',
        
    ])
    if res.returncode != 0:
        raise RuntimeError(f"Agent Failed to Run: {res.stderr}")
    
    # copy the config.py file to the output folder so we can compare config between runs
    shutil.copy(
        os.path.join(test.input_folder, "config.json"),
        os.path.join(test.output_folder, "config.json"),
    )


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
        assert test_parameters.name not in test_names, f"Duplicate test name: {test_parameters.name}"
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

    create_index(os.path.join(config.test_output_directory, "index.html"), tests_to_run)

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
        except Exception as e:
            LOG.exception(
                "test_failed",
                provider=test.provider.name,
                model=test.model,
                test_folder=test.input_folder,
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
