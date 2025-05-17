
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


def generate_html_log_file(test: TestToRun):
    print(test.output_folder)
    stats_file = os.path.join(test.output_folder, "stats.json")
    print(stats_file)
    try:
        stats = open(stats_file, "r")
        stats = ResultStats.model_validate_json(stats.read())
    except Exception as e:
        LOG.exception(
            "failed_to_load_run_stats",
            stats_file=stats_file,
            error=str(e),
        )
        return
    
    log = stats.log
    log_html = generate_log_html(log)
    with open(os.path.join(test.output_folder, "log.html"), "w") as f:
        f.write(log_html)
