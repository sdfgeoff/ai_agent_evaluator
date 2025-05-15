from typing import Any


class Tag:
    def __init__(
        self,
        name: str,
        parent: "Tag | None" = None,
        **kwargs: str | int | float | bool | None,
    ):
        self.attrs = {k.replace("_", ""): v for k, v in kwargs.items()}
        self.name = name
        self.parent = parent
        self.content = ""

    def __enter__(self):
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        if self.parent:
            self.parent.add(self.to_html())

    def to_html(self):
        return f"<{self.name} {self._format_attrs()}>{self.content}</{self.name}>"

    def _format_attrs(self):
        return " ".join(f'{k}="{v}"' for k, v in self.attrs.items() if v is not None)

    def __str__(self):
        return self.to_html()

    def add(self, content: str):
        self.content += content
