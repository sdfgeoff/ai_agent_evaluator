from collections import defaultdict

from agent.datatypes import TestToRun
from .html import Tag
from .test_card import test_card


def test_container(test: str, tests: list[TestToRun]):
    by_provider: dict[str, list[TestToRun]] = defaultdict(list)
    for run in tests:
        provider_name = run.provider.name
        by_provider[provider_name].append(run)

    with Tag("div", None) as test_div:
        with Tag("h1", test_div) as h1:
            h1.add(test)
        with Tag("p", test_div) as p:
            p.add(tests[0].test_parameters.blurb)
        with Tag("p", test_div) as p:
            p.add("Initial Prompt: " + tests[0].test_parameters.initial_prompt)

        for provider, tests in by_provider.items():
            with Tag("h2", test_div) as h2:
                h2.add(provider)
            with Tag("div", test_div, class_="run_container") as run_container:
                for run in tests:
                    run_container.add(test_card(run))
    return str(test_div)
