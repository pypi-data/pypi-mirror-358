from __future__ import annotations

from textwrap import dedent


class Tag:
    """Use Python syntax to emit XML-like documents."""

    def __init__(self, _name: str, _content=[], **attrs):  # noqa: B006
        # allow Python keywords via "x.class_"
        self.name = _name.removesuffix("_")

        # convert "font_width" to "font-width"
        self.attrs = {
            k.removesuffix("_").replace("_", "-"): v for k, v in attrs.items()
        }

        if _content is None:
            # explicitly self-closing
            self.children = None
        elif isinstance(_content, list):
            # empty, appendable
            self.children = _content[:]
        elif isinstance(_content, str):
            # appendable with an initial text node
            self.children = []
            if body := dedent(_content).strip():
                if isinstance(_content, Verbatim):
                    body = Verbatim(body)
                self.children.append(body)

    def __getattr__(self, name):
        def tag_factory(_content=[], **kwargs):  # noqa: B006
            child = Tag(name, _content, **kwargs)
            self(child)
            return child

        return tag_factory

    def __call__(self, child: Tag | Verbatim | str):
        """
        Add a child without wrapping in a tag:

        > parent.child("hi")  # <parent><child>hi</child></parent>
        > parent("hi")  # <parent>hi</parent>
        """
        if self.children is None:
            self.children = []
        self.children.append(child)

    def __enter__(self):
        """Bind the freshly-factored tag to a scoped var."""
        return self

    def __exit__(self, *_):
        pass

    @classmethod
    def _dict_attr(cls, kv: dict):
        """Embed CSS-like attrs."""
        return " ".join(f"{k.replace('_', '-')}: {v};" for k, v in kv.items())

    @staticmethod
    def _(body):
        return Verbatim(body)

    def __str__(self):
        return self._render()

    def _render(self, indent="  "):
        open = "<" + self.name
        for k, v in self.attrs.items():
            open += f' {k}="{self._dict_attr(v) if isinstance(v, dict) else v}"'

        match self.children:
            case None:
                parts = [open + " />\n"]
            case []:
                parts = [open + f"></{self.name}>\n"]
            case _:
                parts = [open + ">\n"]
                for child in self.children:
                    if isinstance(child, Tag):
                        inner = child._render(indent)
                    elif isinstance(child, Verbatim):
                        inner = str(child)
                    else:
                        inner = str(child).replace("<", "&lt;").replace(">", "&gt;")
                    part = "\n".join(indent + line for line in inner.splitlines())
                    parts.append(part + "\n")
                parts.append(f"</{self.name}>\n")

        return "".join(parts)


class Verbatim(str):
    pass


def svg(width, height, min_x=0, min_y=0, **kwargs):
    return Tag(
        "svg",
        xmlns="http://www.w3.org/2000/svg",
        viewBox=f"{min_x} {min_y} {width} {height}",
        width=width,
        height=height,
        **kwargs,
    )
