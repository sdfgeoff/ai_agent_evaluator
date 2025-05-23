import os
from ..agent.datatypes import TestToRun
from .html import Tag


def run_card(source_page: str, run: TestToRun):
    relpath = os.path.relpath(
        run.output_folder,
        start=os.path.dirname(source_page),
    )
    with Tag("div", class_="run_card") as run_div:
        with Tag("h4", run_div) as h2:
            h2.add(run.model.key)
        # iframe of output_folder.index.html
        with Tag("div", run_div, class_="zoom-outer") as zoom_div_outer:
            with Tag("div", zoom_div_outer, class_="zoom-inner") as zoom_div:
                with Tag(
                    "iframe",
                    zoom_div,
                    src=f"{relpath}/index.html",
                    width="1920",
                    height="1080",
                ):
                    pass
        with Tag("div", run_div, class_="d-flex") as footer:
            with Tag("div", footer) as fullscreen:
                with Tag("a", fullscreen, href=f"{relpath}/index.html") as a:
                    a.add("Fullscreen")
            
            with Tag("div", footer, class_="flex-grow-1") as gap:
                pass
            
            with Tag("div", footer) as message_log:
                with Tag("a", message_log, href=f"{relpath}/log.html") as a:
                    a.add("Message Log")

    return str(run_div)
