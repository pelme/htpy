import textwrap

import pytest

from htpy.html2htpy import BlackFormatter, RuffFormatter, html2htpy


def test_convert_default_shorthand_id_and_class():
    input = """
        <div id="div-id" class="some-class other-class">
          <p>This is a paragraph.</p>
        </div>
    """

    actual = html2htpy(input)
    expected = 'div("#div-id.some-class.other-class")[p["This is a paragraph."]]'

    assert actual == expected


def test_convert_explicit_id_class_syntas():
    input = """
        <div id="div-id" class="some-class other-class">
          <p>This is a paragraph.</p>
        </div>
    """

    actual = html2htpy(input, shorthand_id_class=False)
    expected = 'div(id="div-id",class_="some-class other-class")[p["This is a paragraph."]]'

    assert actual == expected


nested_html = """
    <div>
      <p>This is a <span>nested</span> element.</p>
      <p>Another <a href="#">nested <strong>tag</strong></a>.</p>
    </div>
"""


def test_convert_nested_element_without_formatting():
    actual = html2htpy(nested_html, formatter=None)

    expected = (
        "div["
        'p["This is a ",span["nested"]," element."],'
        'p["Another ",a(href="#")["nested ",strong["tag"]],"."]'
        "]"
    )

    assert actual == expected


def test_convert_nested_element_ruff_formatting():
    actual = html2htpy(nested_html, formatter=RuffFormatter())
    assert actual == textwrap.dedent(
        """\
        div[
            p["This is a ", span["nested"], " element."],
            p["Another ", a(href="#")["nested ", strong["tag"]], "."],
        ]
        """
    )


def test_convert_nested_element_black_formatting():
    actual = html2htpy(nested_html, formatter=BlackFormatter())
    assert actual == textwrap.dedent(
        """\
        div[
            p["This is a ", span["nested"], " element."],
            p["Another ", a(href="#")["nested ", strong["tag"]], "."],
        ]
        """
    )


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

    actual = html2htpy(input)
    expected = r'p[f"{ variable } is \"a\" {{ paragraph }}."]'

    assert actual == expected


def test_convert_f_string_escaping_complex():
    input = """
    <body>
      <h1>{{ heading }}</h1>
      <p>Welcome to our cooking site, {{ user.name }}!</p>

      <h2>Recipe of the Day: {{ recipe.name }}</h2>
      <p>{{ recipe.description }}</p>

      <h3>Instructions:</h3>
      <ol>
          {% for step in recipe.steps %}
          <li>{{ step }}</li>
          {% endfor %}
      </ol>
    </body>
    """

    actual = html2htpy(input, formatter=RuffFormatter())
    expected = textwrap.dedent(
        """\
        body[
            h1[f"{ heading }"],
            p[f"Welcome to our cooking site, { user.name }!"],
            h2[f"Recipe of the Day: { recipe.name }"],
            p[f"{ recipe.description }"],
            h3["Instructions:"],
            ol[
                \"\"\"          {% for step in recipe.steps %}          \"\"\",
                li[f"{ step }"],
                \"\"\"          {% endfor %}      \"\"\",
            ],
        ]
    """
    )

    assert actual == expected


def test_convert_script_tag():
    input = """
        <script type="text/javascript">alert('This is a script');</script>
    """

    actual = html2htpy(input)
    assert actual == """script(type="text/javascript")["alert('This is a script');"]"""


def test_convert_style_tag():
    input = """
        <style>body { background-color: #fff; }</style>
    """
    actual = html2htpy(input)
    assert actual == """style["body { background-color: #fff; }"]"""


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
    expected = """html[head[title["Test Document"]],body[h1["Header"],p["Paragraph"]]]"""

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
    assert actual == """[input(type="checkbox",checked=True),option(selected=True)["Option"]]"""


def test_convert_complex_section():
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

    actual = html2htpy(input, shorthand_id_class=False, formatter=BlackFormatter())
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


def test_convert_complex_svg():
    path_d: str = (
        "m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2"
        ".652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1"
        ".13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8."
        "932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.2"
        "5 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75"
        "V8.25A2.25 2.25 0 0 1 5.25 6H10"
    )

    input = f"""
        <svg
          xmlns="http://www.w3.org/2000/svg"
          fill="none" viewBox="0 0 24 24"
          stroke-width="1.5"
          stroke="currentColor"
          class="w-6 h-6">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              d="{path_d}"
            />
        </svg>
    """

    actual_output = html2htpy(input, formatter=BlackFormatter())

    expected_output = textwrap.dedent(
        f"""\
            svg(
                ".w-6.h-6",
                xmlns="http://www.w3.org/2000/svg",
                fill="none",
                viewbox="0 0 24 24",
                stroke_width="1.5",
                stroke="currentColor",
            )[
                path(
                    stroke_linecap="round",
                    stroke_linejoin="round",
                    d="{path_d}",
                )
            ]
        """
    )

    assert expected_output == actual_output
