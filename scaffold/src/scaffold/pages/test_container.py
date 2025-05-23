from collections import defaultdict

from ..agent.datatypes import TestToRun
from .html import Tag
from .run_card import run_card


def test_container(source_page: str, test: str, tests: list[TestToRun]):
    by_provider: dict[str, list[TestToRun]] = defaultdict(list)
    for run in tests:
        provider_name = run.provider.name
        by_provider[provider_name].append(run)

    provider_names = sorted(by_provider.keys())

    with Tag("div", None, id=f"test-{test}", class_="") as test_div:
        with Tag("div", test_div, class_="panel") as test_heading:
            with Tag(
                "a", test_heading, href=f"#{test}", class_="no-link-underline"
            ) as a:
                with Tag("h2", a) as h1:
                    h1.add(tests[0].test_parameters.name)
            
            with Tag("div", test_heading, class_="d-flex gap-1") as tag_container:
                for tag in tests[0].test_parameters.tags:
                    with Tag("div", tag_container, class_="tag") as div:
                        div.add(tag)
        with Tag("div", test_div, class_="panel-light") as test_header:
            with Tag("p", test_header) as p:
                p.add(tests[0].test_parameters.blurb)
            with Tag("h3", test_header) as p:
                p.add("Initial Prompt:")
            for prompt in tests[0].test_parameters.initial_prompt:
                with Tag("pre", test_header, class_="prompt") as p:
                    p.add(prompt.content)

        for provider in provider_names:
            tests = sorted(by_provider[provider], key=lambda x: x.model.key)

            with Tag("h3", test_div) as h2:
                h2.add(provider)
            with Tag("div", test_div, class_="run_container padding-1 d-flex gap-1") as run_container:
                for run in tests:
                    run_container.add(run_card(source_page, run))
    return str(test_div)
