from collections import defaultdict
from ..agent.datatypes import TestToRun

from .html import Tag
from .test_container import test_container


def index_html(
    source_page: str,
    tests: list[TestToRun],
) -> str:
    by_test_name: dict[str, list[TestToRun]] = defaultdict(list)
    for test in tests:
        test_name = test.test_parameters.name
        by_test_name[test_name].append(test)

    # sort test by test name
    test_names = sorted(by_test_name.keys())

    with Tag("html") as html:
        with Tag("head", html) as head:
            with Tag("title", head) as title:
                title.add("Evaluation Results")
            with Tag("style", head) as style:
                style.add(
                    """
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #e0e0e0;
                    }
                    .pagecontainer {
                        margin: auto;
                        background-color: #f4f4f4;
                        width: 84em;
                        padding: 2em;
                    }
                    h1 {
                        color: #333;
                    }
                    .zoom-outer {
                        width: 240px;
                        height: 135px;
                        background-color: #fff;
                    }
                    .zoom-inner {
                        transform: scale(0.125);
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

                    .prompt {
                        white-space: pre-wrap;
                        background-color: #000;
                        color: #fff;
                        border-radius: 5px;
                        padding: 10px;
                        margin-bottom: 20px;
                    }

                    .no-link-underline {
                        color: #000;
                        text-decoration: none;
                    }
                    .no-link-underline:hover {
                        text-decoration: underline;
                    }

                    .panel {
                        margin: 0 -2em 0 -2em;
                        padding: 1em 2em 1em 2em;
                        background-color: #FFC067;
                    }
                    .panel-light {
                        margin: 0 -2em 0 -2em;
                        padding: 1em 2em 1em 2em;
                        background-color: #FFe0B2;
                    }

                    .d-flex {
                        display: flex;
                    }
                    .flex-grow-1 {
                        flex-grow: 1;
                    }

                    """
                )
        with Tag("body", html) as body:
            with Tag("div", body, class_="pagecontainer") as pagecontainer:
                with Tag("h1", pagecontainer) as h1:
                    h1.add("Simple Agent Benchmark")
                with Tag("h2", pagecontainer) as h2:
                    h2.add("What is this?")
                with Tag("p", pagecontainer) as p:
                    p.add(
                        "As AI's get better and better, benchmarking them becomes fuzzier and fuzzier. While in the past 'do this computation' was good enough, now we "
                        "can give them much more abstract tasks. This page attempts to solve this problem by using visual bencmarks - somethig that is easy for a human to compare. This allows the agent to take creative license and produce a result that is observably 'good' rather than provably 'correct'."
                    )
                with Tag("p", pagecontainer) as p:
                    p.add(
                        "Technically, this project takes the form of a very very simple agent. The agent is just a loop that takes an initial prompt and an initial set of files, and then runs the AI on them, providing the agent with some simple tools and 100 iterations. "
                        "To judge the results, it is expectd that the test will output an index.html file, which will be embedded here. To aid in figuring out what is going on, the complete message log is also available, and can be viewed by clicking the 'View Message Log' link."
                    )

                with Tag("h2", pagecontainer) as h2:
                    h2.add("Table of Contents")
                with Tag("ul", pagecontainer) as ul:
                    for test in test_names:
                        with Tag("li", ul) as li:
                            with Tag("a", li, href=f"#test-{test}") as a:
                                a.add(test)

                with Tag("h1", pagecontainer) as h2:
                    h2.add("Results")

                for test in test_names:
                    tests = by_test_name[test]
                    pagecontainer.add(test_container(source_page, test, tests))

    return str(html)
