import textwrap
import pytest
from htpy.html2htpy import html2htpy


def test_convert_shorthand_id_and_class():
    input = """
        <div id="div-id" class="some-class other-class">
          <p>This is a paragraph.</p>
        </div>
    """

    actual = html2htpy(input, shorthand_id_class=True, format=True)
    expected = 'div("#div-id.some-class.other-class")[p["This is a paragraph."]]\n'

    assert actual == expected


def test_convert_nested_element():
    input = """
    <div>
      <p>This is a <span>nested</span> element.</p>
      <p>Another <a href="#">nested <strong>tag</strong></a>.</p>
    </div>
    """

    actual = html2htpy(input, format=True)
    expected = textwrap.dedent(
        """\
        div[
            p["This is a ", span["nested"], " element."],
            p["Another ", a(href="#")["nested ", strong["tag"]], "."],
        ]
        """
    )

    assert actual == expected


def test_convert_self_closing_tags():
    input = """
        <img src="image.jpg" alt="An image" />
        <br />
        <input type="text" />
    """

    actual = html2htpy(input)

    assert actual == '[img(src="image.jpg",alt="An image"),br,input(type="text")]'


def test_convert_attribute_with_special_characters():
    input = """<img src="path/to/image.jpg" alt="A <test> & 'image'" />"""
    actual = html2htpy(input)
    assert actual == """img(src="path/to/image.jpg",alt="A <test> & 'image'")"""


def test_convert_ignores_comments():
    input = """
    <!-- This is a comment -->
    <div>Content <!-- Another comment --> inside</div>
    """
    actual = html2htpy(input)
    assert actual == 'div["Content "," inside"]'


def test_convert_special_characters():
    input = """
    <p>Special characters: &amp; &lt; &gt; &quot; &apos; &copy;</p>
    """

    actual = html2htpy(input)
    assert actual == 'p["Special characters: & < > \\" \' ©"]'


def test_convert_f_string_escaping():
    input = """
        <p>{{ variable }} is "a" { paragraph }.</p>
    """

    actual = html2htpy(input, format=False)
    expected = r'p[f"{ variable } is \"a\" {{ paragraph }}."]'

    assert actual == expected


def test_convert_script_style_tags():
    input = """
        <script type="text/javascript">alert('This is a script');</script>
        <style>body { background-color: #fff; }</style>
    """

    actual = html2htpy(input, format=True)
    assert actual == textwrap.dedent(
        """\
        [
            script(type="text/javascript")["alert('This is a script');"],
            style["body { background-color: #fff; }"],
        ]
        """
    )


def test_convert_html_doctype():
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

    actual = html2htpy(input)
    expected = (
        """html[head[title["Test Document"]],body[h1["Header"],p["Paragraph"]]]"""
    )

    assert actual == expected


def test_convert_empty_elements():
    input = """
        <div></div>
        <p></p>
        <span></span>
    """

    actual = html2htpy(input)
    assert actual == "[div,p,span]"


def test_convert_custom_tag():
    input = """
        <custom-element attribute="value">Custom content</custom-element>
    """

    actual = html2htpy(input)
    assert actual == """custom_element(attribute="value")["Custom content"]"""


def test_convert_malformed_html():
    input = """
        <div>
          <p>Paragraph without closing tag
          <div>Another div</p>
        </div>
    """

    with pytest.raises(Exception) as e:
        html2htpy(input)

    assert "Closing tag p does not match the currently open tag (div)" in str(e.value)


def test_convert_attributes_without_values():
    input = """
        <input type="checkbox" checked />
        <option selected>Option</option>
    """
    actual = html2htpy(input)
    assert (
        actual
        == """[input(type="checkbox",checked=True),option(selected=True)["Option"]]"""
    )


def test_convert_section_regular():
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

    actual = html2htpy(input, shorthand_id_class=False, format=True)
    expected = textwrap.dedent(
        """\
        section(class_="hero is-fullheight is-link")[
            div(class_="hero-body")[
                div(class_="container")[
                    p(class_="subtitle is-3 is-spaced")["Welcome"],
                    p(class_="title is-1 is-spaced")[f"Student code: {student_code}"],
                ]
            ]
        ]
        """
    )

    assert actual == expected


def test_convert_section_shorthand_id_class():
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

    actual = html2htpy(input, shorthand_id_class=True, format=True)

    assert actual == textwrap.dedent(
        """\
        section(".hero.is-fullheight.is-link")[
            div(".hero-body")[
                div(".container")[
                    p(".subtitle.is-3.is-spaced")["Welcome"],
                    p(".title.is-1.is-spaced")[f"Student code: {student_code}"],
                ]
            ]
        ]
        """
    )


def test_convert_nested_element_without_formatting():
    input = """
        <div>
          <p>This is a <span>nested</span> element.</p>
          <p>Another <a href="#">nested <strong>tag</strong></a>.</p>
        </div>
    """

    actual = html2htpy(input, format=False)

    expected = 'div[p["This is a ",span["nested"]," element."],p["Another ",a(href="#")["nested ",strong["tag"]],"."]]'

    assert actual == expected


def test_convert_html_to_htpy_svg():
    input = """
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
        </svg>
    """

    actual_output = html2htpy(input, format=True)

    expected_output = textwrap.dedent(
        """\
            svg(
                xmlns="http://www.w3.org/2000/svg",
                fill="none",
                viewbox="0 0 24 24",
                stroke_width="1.5",
                stroke="currentColor",
                class_="w-6 h-6",
            )[
                path(
                    stroke_linecap="round",
                    stroke_linejoin="round",
                    d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10",
                )
            ]
        """
    )

    assert expected_output == actual_output
