
import os
import shutil
import subprocess

from .log_to_html import generate_log_html
from .pages.index_html import index_html
from .agent.datatypes import ResultStats, TestToRun
import structlog

LOG = structlog.get_logger(__name__)


def create_site(output_file: str, tests: list[TestToRun]):
    html = index_html(output_file, tests)
    with open(output_file, "w") as f:
        f.write(str(html))


def run_test(
    agent_binary: str,
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
    agent_folder = os.path.dirname(agent_binary)
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
            f"/agent/{os.path.basename(agent_binary)}",
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
