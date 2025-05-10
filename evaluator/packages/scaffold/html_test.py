from html import Tag

def test_html():
    with Tag("html", None) as html:
        with Tag("body", html) as body:
            with Tag("div", body, class_="block") as div:
                div.add("Hello, World!")
    assert str(html) == '<html ><body ><div class="block">Hello, World!</div></body></html>'
