from textwrap import dedent

import exml


def test_tags():
    root = exml.Tag("root", x_r="r")
    body = root.body(b="b")
    body.test("yo", a1="a1")
    t2 = body.test("hai", a2="a2")
    t2.empty_()
    body.selfclosing(None, nope=None)
    body.escaped("<!-- no surprise -->")
    body.verbatim(t2._("<!-- surprise -->"))
    body("bye!")

    doc = """
    <root x-r="r">
      <body b="b">
        <test a1="a1">
          yo
        </test>
        <test a2="a2">
          hai
          <empty></empty>
        </test>
        <selfclosing nope="None" />
        <escaped>
          &lt;!-- no surprise --&gt;
        </escaped>
        <verbatim>
          <!-- surprise -->
        </verbatim>
        bye!
      </body>
    </root>
    """

    assert str(root).strip() == dedent(doc).strip()


def test_tags_ctx():
    html = exml.Tag("html")
    with html.body().table(width="100%") as t:
        with t.tr(class_="fancy") as row:
            row.td("a")
            row.td("b")
        with t.tr(style={"color": "red"}) as row:
            row.attrs["style"]["width"] = 123
            row.td("x")
            row.td("y")

    doc = """
    <html>
      <body>
        <table width="100%">
          <tr class="fancy">
            <td>
              a
            </td>
            <td>
              b
            </td>
          </tr>
          <tr style="color: red; width: 123;">
            <td>
              x
            </td>
            <td>
              y
            </td>
          </tr>
        </table>
      </body>
    </html>
    """

    assert str(html).strip() == dedent(doc).strip()
