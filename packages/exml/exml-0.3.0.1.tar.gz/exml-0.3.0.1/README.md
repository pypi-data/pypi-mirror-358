# eXML

A tiny eDSL to generate HTML/SVG/XML-looking strings.

## Example

> See tests for more code and output.

```python
import exml

html = exml.Tag("html")
with html.body().table(width="100%") as t:
    with t.tr(class_="fancy") as row:
        row.td("a")
        row.td("b")
    with t.tr(style={"color": "red"}) as row:
        row.attrs["style"]["width"] = 123
        row.td("x")
        row.td("y")
print(str(html))
```
