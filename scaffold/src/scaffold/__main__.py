import json
import os
from pydantic import BaseModel

from .test import create_site, generate_html_log_file, run_test


from .config import get_config
from .agent.datatypes import TestConfig, TestToRun
import structlog
import argparse

LOG = structlog.get_logger(__name__)




class Args(BaseModel):
    agent_binary: str
    input_directory: str
    output_directory: str


def main(args: Args):
    config = get_config()
    providers = config.providers
    test_folders = os.listdir(args.input_directory)

    tests_to_run: list[TestToRun] = []
    test_names: list[str] = []
    for test_folder in test_folders:
        test_settings_file = os.path.join(
            args.input_directory, test_folder, "config.json"
        )
        if not os.path.exists(test_settings_file):
            LOG.error(
                "test_config_not_found",
                test_folder=test_folder,
                test_settings_file=test_settings_file,
            )
            continue
        else:
            LOG.info(
                "loading_test",
                test_settings_file=test_settings_file,
            )
        test_parameters = TestConfig.model_validate(
            json.load(open(test_settings_file, "r"))
        )
        assert test_parameters.name not in test_names, (
            f"Duplicate test name: {test_parameters.name}"
        )
        test_names.append(test_parameters.name)

        for provider in providers:
            for model in provider.models:
                output_folder = os.path.join(
                    os.path.abspath(args.output_directory),
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
                            args.input_directory, test_folder
                        ),
                        output_folder=output_folder,
                    )
                )

    # Sort by provider name and model name
    tests_to_run.sort(key=lambda x: (x.provider.name, x.model))

    create_site(os.path.join(args.output_directory, "index.html"), tests_to_run)

    for test in tests_to_run:
        existing_config_file = os.path.join(test.output_folder, "config.json")

        skip = False
        if os.path.exists(existing_config_file):
            with open(existing_config_file, "r") as f:
                existing_config = f.read()
            with open(os.path.join(test.input_folder, "config.json"), "r") as f:
                new_config = f.read()

            if existing_config == new_config:
                skip = True

        if not skip:
            try:
                run_test(args.agent_binary, test)
            except Exception as _e:
                LOG.exception(
                    "test_failed",
                    provider=test.provider.name,
                    model=test.model,
                    test_folder=test.input_folder,
                )
        else:
            LOG.info(
                "skipping_test",
                provider=test.provider.name,
                model=test.model,
                test_folder=test.input_folder,
                output_folder=test.output_folder,
            )        

        if os.path.exists(os.path.join(test.output_folder, "stats.json")):
            generate_html_log_file(test)


def run():
    parser = argparse.ArgumentParser(description="Run the AI Agent Evaluator.")
    parser.add_argument(
        "--agent-binary", help="Path to the agent binary")
    parser.add_argument(
        "--input-directory",
        help="Path to the test input directory",
        default=os.path.join(os.path.dirname(__file__), "inputs"),
    )
    parser.add_argument(
        "--output-directory",
        help="Path to the test output directory",
        default=os.path.join(os.path.dirname(__file__), "outputs"),
    )
    args = parser.parse_args()

    args_parsed = Args(
        agent_binary=os.path.abspath(args.agent_binary),
        input_directory=os.path.abspath(args.input_directory),
        output_directory=os.path.abspath(args.output_directory),
    )
    LOG.info(
        "args_parsed",
        args=args_parsed.model_dump(),
    )


    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    main(args_parsed)


if __name__ == "__main__":
    run()
