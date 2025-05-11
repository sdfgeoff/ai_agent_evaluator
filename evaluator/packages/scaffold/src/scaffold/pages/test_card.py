from agent.datatypes import TestToRun
from .html import Tag


def test_card(run: TestToRun):
    with Tag("div", class_="run_card") as run_div:
        with Tag("h2", run_div) as h2:
            h2.add(run.model)
        # iframe of output_folder.index.html
        with Tag("div", run_div, class_="zoom-outer") as zoom_div_outer:
            with Tag("div", zoom_div_outer, class_="zoom-inner") as zoom_div:
                with Tag(
                    "iframe",
                    zoom_div,
                    src=f"{run.output_folder}/index.html",
                    width="1920",
                    height="1080",
                ):
                    pass
        with Tag("a", run_div, href=f"{run.output_folder}/index.html") as a:
            a.add("View Full Size")
        run_div.add(" ")
        with Tag("a", run_div, href=f"{run.output_folder}/log.html") as a:
            a.add("View Message Log")

    return str(run_div)
