import json
import os
from pydantic import BaseModel

from .test import create_site, generate_html_log_file

from .agent.datatypes import TestConfig, TestToRun
import structlog
import argparse

LOG = structlog.get_logger(__name__)


class Args(BaseModel):
    output_directory: str


def find_files_by_name_in_directory(
    directory: str, name: str
) -> list[str]:
    """
    Find all files with the given name in the directory and its subdirectories.
    """
    matches = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file == name:
                matches.append(os.path.join(root, file))
    return matches


def main(args: Args):
    run_config_paths = find_files_by_name_in_directory(
        os.path.abspath(args.output_directory), "test.json"
    )

    # load all the run configs
    test_to_run_configs: list[TestToRun] = []
    for run_config in run_config_paths:
        try:
            run_config = TestToRun.model_validate(
                json.load(open(run_config, "r"))
            )
            test_to_run_configs.append(run_config)
        except Exception as e:
            LOG.error(
                "failed_to_load_test_config",
                run_config=run_config,
                error=str(e),
            )
            continue

    create_site(os.path.join(args.output_directory, "index.html"), test_to_run_configs)

    for test in test_to_run_configs:
        generate_html_log_file(test)


def run():
    parser = argparse.ArgumentParser(description="Run the AI Agent Evaluator.")
    parser.add_argument(
        "--output-directory",
        help="Path to the test output directory",
        default=os.path.join(os.path.dirname(__file__), "outputs"),
    )
    args = parser.parse_args()

    args_parsed = Args(
        output_directory=os.path.abspath(args.output_directory),
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
    LOG.info(
        "args_parsed",
        args=args_parsed.model_dump(),
    )
    main(args_parsed)


if __name__ == "__main__":
    run()
