import textwrap

import pytest

from htpy.html2htpy import BlackFormatter, RuffFormatter, html2htpy


def test_convert_default_shorthand_id_and_class() -> None:
    input = """
        <div id="div-id" class="some-class other-class">
            <p>This is a paragraph.</p>
        </div>
    """

    actual = html2htpy(input, import_mode="no")
    expected = 'div("#div-id.some-class.other-class")[p["This is a paragraph."]]'

    assert actual == expected


def test_convert_explicit_id_class_syntas() -> None:
    input = """
        <div id="div-id" class="some-class other-class">
            <p>This is a paragraph.</p>
        </div>
    """

    actual = html2htpy(input, shorthand_id_class=False, import_mode="no")
    expected = 'div(id="div-id", class_="some-class other-class")[p["This is a paragraph."]]'

    assert actual == expected


nested_html = """
    <div>
        <p>This is a <span>nested</span> element.</p>
        <p>Another <a href="#">nested <strong>tag</strong></a>.</p>
    </div>
"""


def test_convert_nested_element_without_formatting() -> None:
    actual = html2htpy(nested_html, formatter=None, import_mode="no")

    expected = (
        "div["
        'p["This is a ", span["nested"], " element."], '
        'p["Another ", a(href="#")["nested ", strong["tag"]], "."]'
        "]"
    )

    assert actual == expected


def test_convert_nested_element_ruff_formatting() -> None:
    actual = html2htpy(nested_html, formatter=RuffFormatter(), import_mode="no")
    assert actual == textwrap.dedent(
        """\
        div[
            p["This is a ", span["nested"], " element."],
            p["Another ", a(href="#")["nested ", strong["tag"]], "."],
        ]
        """
    )


def test_convert_nested_element_black_formatting() -> None:
    actual = html2htpy(nested_html, formatter=BlackFormatter(), import_mode="no")
    assert actual == textwrap.dedent(
        """\
        div[
            p["This is a ", span["nested"], " element."],
            p["Another ", a(href="#")["nested ", strong["tag"]], "."],
        ]
        """
    )


def test_convert_nested_element___import_mode_yes() -> None:
    actual = html2htpy(nested_html, import_mode="yes")
    assert actual == (
        "from htpy import a, div, p, span, strong\n"
        "div["
        'p["This is a ", span["nested"], " element."], '
        'p["Another ", a(href="#")["nested ", strong["tag"]], "."]'
        "]"
    )


def test_convert_nested_element___import_mode_h() -> None:
    actual = html2htpy(nested_html, import_mode="h")
    assert actual == (
        "import htpy as h\n"
        "h.div["
        'h.p["This is a ", h.span["nested"], " element."], '
        'h.p["Another ", h.a(href="#")["nested ", h.strong["tag"]], "."]'
        "]"
    )


def test_convert_custom_element_include_imports() -> None:
    input = '<custom-element attribute="value">Custom content</custom-element>'
    actual = html2htpy(input, import_mode="yes")

    assert actual == (
        'from htpy import custom_element\ncustom_element(attribute="value")["Custom content"]'
    )


def test_convert_self_closing_tags() -> None:
    input = """
        <img src="image.jpg" alt="An image" />
        <br />
        <input type="text" />
    """

    actual = html2htpy(input, import_mode="no")

    assert actual == '[img(src="image.jpg", alt="An image"),br,input(type="text")]'


def test_convert_attribute_with_special_characters() -> None:
    input = """<img src="path/to/image.jpg" alt="A <test> & 'image'" />"""
    actual = html2htpy(input, import_mode="no")
    assert actual == """img(src="path/to/image.jpg", alt="A <test> & 'image'")"""


def test_convert_ignores_comments() -> None:
    input = """
    <!-- This is a comment -->
    <div>Content <!-- Another comment --> inside</div>
    """
    actual = html2htpy(input, import_mode="no")
    assert actual == 'div["Content ", " inside"]'


def test_convert_special_characters() -> None:
    input = """
    <p>Special characters: &amp; &lt; &gt; &quot; &apos; &copy;</p>
    """

    actual = html2htpy(input, import_mode="no")
    assert actual == 'p["Special characters: & < > \\" \' ©"]'


def test_convert_f_string_escaping() -> None:
    input = """
        <p>{{ variable }} is "a" { paragraph } {{ variable.with.attrib }}.</p>
    """

    actual = html2htpy(input, import_mode="no")
    expected = r'p[f"{ variable } is \"a\" {{ paragraph }} { variable.with.attrib }."]'

    assert actual == expected


def test_convert_script_tag() -> None:
    input = """
        <script type="text/javascript">alert('This is a script');</script>
    """

    actual = html2htpy(input, import_mode="no")
    assert actual == """script(type="text/javascript")["alert('This is a script');"]"""


def test_convert_style_tag() -> None:
    input = """
        <style>body { background-color: #fff; }</style>
    """
    actual = html2htpy(input, import_mode="no")
    assert actual == """style["body { background-color: #fff; }"]"""


def test_convert_html_doctype() -> None:
    input = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Document</title>
        </head>
        <body>
            <h1>Header</h1>
            <p>Paragraph</p>
        </body>
        </html>
    """

    actual = html2htpy(input, import_mode="no")
    expected = """html[head[title["Test Document"]], body[h1["Header"], p["Paragraph"]]]"""

    assert actual == expected


def test_convert_empty_elements() -> None:
    input = """
        <div></div>
        <p></p>
        <span></span>
    """

    actual = html2htpy(input, import_mode="no")
    assert actual == "[div,p,span]"


def test_convert_void_elements() -> None:
    input = """
        <div>
        <div>
            <input type="text" />
        </div>

        <div>
            <input type="text">
        </div>
    </div>
    """

    actual = html2htpy(input, import_mode="no")
    assert actual == 'div[div[input(type="text")], div[input(type="text")]]'


def test_convert_custom_tag() -> None:
    input = """
        <custom-element attribute="value">Custom content</custom-element>
    """

    actual = html2htpy(input, import_mode="no")
    assert actual == """custom_element(attribute="value")["Custom content"]"""


def test_convert_malformed_html() -> None:
    input = """
        <div>
            <p>Paragraph without closing tag
            <div>Another div</p>
        </div>
    """

    with pytest.raises(Exception) as e:
        html2htpy(input)

    assert "Closing tag p does not match the currently open tag (div)" in str(e.value)


def test_convert_attributes_without_values() -> None:
    input = """
        <input type="checkbox" checked />
        <option selected>Option</option>
    """
    actual = html2htpy(input, import_mode="no")
    assert actual == """[input(type="checkbox", checked=True),option(selected=True)["Option"]]"""


def test_convert_complex_section() -> None:
    input = """
        <section class="hero is-fullheight is-link">
            <div class="hero-body">
                <div class='container'>
                    <p class="subtitle is-3 is-spaced">Welcome</p>
                    <p class="title is-1 is-spaced">Student code: {{student_code}}</p>
                </div>
            </div>
        </section>
    """

    actual = html2htpy(input, shorthand_id_class=False, import_mode="no")
    expected = (
        'section(class_="hero is-fullheight is-link")['
        'div(class_="hero-body")['
        'div(class_="container")['
        'p(class_="subtitle is-3 is-spaced")["Welcome"], '
        'p(class_="title is-1 is-spaced")[f"Student code: {student_code}"]'
        "]"
        "]"
        "]"
    )

    assert actual == expected


def test_reserved_keyword_attributes() -> None:
    actual = html2htpy('<img class="foo" del="x">', shorthand_id_class=False, import_mode="no")
    expected = 'img(class_="foo", del_="x")'

    assert actual == expected


def test_dict_attributes() -> None:
    actual = html2htpy(
        '<img src="bar.gif" @a-b="c" @d>',
        shorthand_id_class=False,
        import_mode="no",
    )
    expected = 'img(src="bar.gif", {"@a-b": "c", "@d": True})'

    assert actual == expected


def test_shorthand_contains_hashtag() -> None:
    actual = html2htpy(
        '<div id="a" class="bg-gradient-to-tr from-[#ff80b5] to-[#9089fc]"></div>',
        shorthand_id_class=True,
        import_mode="no",
    )

    assert actual == 'div(id="a", class_="bg-gradient-to-tr from-[#ff80b5] to-[#9089fc]")'


def test_shorthand_contains_dot() -> None:
    actual = html2htpy(
        '<div id="a" class="w-[50.0625rem]"></div>',
        shorthand_id_class=True,
        import_mode="no",
    )

    assert actual == 'div(id="a", class_="w-[50.0625rem]")'


def test_del_tag_is_replaced_with_del_() -> None:
    actual = html2htpy(
        "<div><del>deleted</del></div>",
        shorthand_id_class=True,
        import_mode="yes",
    )

    assert actual == 'from htpy import del_, div\ndiv[del_["deleted"]]'


def test_convert_stripping_simple_whitespace() -> None:
    actual = html2htpy(
        "<p>      \t\t\nHi\n\n\t  </p>",
        import_mode="no",
    )

    assert actual == 'p["Hi"]'


def test_convert_pre_element_retains_all_whitespace() -> None:
    actual = html2htpy(
        textwrap.dedent(
            """\
            <pre>
            hello,   fellow   programmer.

            This   element   retains   newlines   and   whitespace.
            </pre>
            """
        ),
        import_mode="no",
    )

    assert actual == textwrap.dedent(
        '''\
        pre["""hello,   fellow   programmer.

        This   element   retains   newlines   and   whitespace."""]'''
    )
