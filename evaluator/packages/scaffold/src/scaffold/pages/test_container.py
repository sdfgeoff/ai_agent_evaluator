from collections import defaultdict

from agent.datatypes import TestToRun
from .html import Tag
from .run_card import run_card


def test_container(test: str, tests: list[TestToRun]):
    by_provider: dict[str, list[TestToRun]] = defaultdict(list)
    for run in tests:
        provider_name = run.provider.name
        by_provider[provider_name].append(run)

    provider_names = sorted(by_provider.keys())

    with Tag("div", None, id=f"test-{test}", class_="") as test_div:
        with Tag("div", test_div, class_="panel") as test_heading:
            with Tag("a", test_heading, href=f"#{test}", class_="no-link-underline") as a:
                with Tag("h2", a) as h1:
                    h1.add(test)
        with Tag("div", test_div, class_="panel-light") as test_header:
            with Tag("p", test_header) as p:
                p.add(tests[0].test_parameters.blurb)
            with Tag("h3", test_header) as p:
                p.add("Initial Prompt:")
            with Tag("pre", test_header, class_="prompt") as p:
                p.add(tests[0].test_parameters.initial_prompt)

        for provider in provider_names:
            tests = sorted(by_provider[provider], key=lambda x: x.model)

            with Tag("h3", test_div) as h2:
                h2.add(provider)
            with Tag("div", test_div, class_="run_container") as run_container:
                for run in tests:
                    run_container.add(run_card(run))
    return str(test_div)
