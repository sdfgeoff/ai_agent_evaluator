from collections import defaultdict
from agent.datatypes import TestToRun

from .html import Tag
from .test_container import test_container


def index_html(
    tests: list[TestToRun],
) -> str:
    by_test_name: dict[str, list[TestToRun]] = defaultdict(list)
    for test in tests:
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
                body.add(test_container(test, tests))

    return str(html)
