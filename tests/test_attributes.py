from htpy import button, div


def test_attribute() -> None:
    assert str(div(id="hello")["hi"]) == '<div id="hello">hi</div>'


def test_class_str() -> None:
    result = div(class_=">foo bar")
    assert str(result) == '<div class="&gt;foo bar"></div>'


def test_class_list() -> None:
    result = div(class_=[">foo", False, None, "", "bar"])
    assert str(result) == '<div class="&gt;foo bar"></div>'


def test_class_dict() -> None:
    result = div(class_={">foo": True, "x": False, "y": None, "z": "", "bar": True})
    assert str(result) == '<div class="&gt;foo bar"></div>'


def test_dict_attributes() -> None:
    result = div({"@click": 'hi = "hello"'})
    assert str(result) == """<div @click="hi = &quot;hello&quot;"></div>"""


def test_underscore() -> None:
    # Hyperscript (https://hyperscript.org/) uses _, make sure it works good.
    result = div(_="foo")
    assert str(result) == """<div _="foo"></div>"""


def test_dict_attributes_avoid_replace() -> None:
    result = div({"class_": "foo", "hello_hi": "abc"})
    assert str(result) == """<div class_="foo" hello_hi="abc"></div>"""


def test_dict_attribute_false() -> None:
    result = div({"bool-false": False})
    assert str(result) == "<div></div>"


def test_dict_attribute_true() -> None:
    result = div({"bool-true": True})
    assert str(result) == "<div bool-true></div>"


def test_underscore_replacement() -> None:
    result = button(hx_post="/foo")["click me!"]
    assert str(result) == """<button hx-post="/foo">click me!</button>"""


def test_escape_attribute_name() -> None:
    result = div({"<disturbing attr>": "value"})
    assert str(result) == """<div &lt;disturbing attr&gt;="value"></div>"""


def test_boolean_attribute_true() -> None:
    result = button(disabled=True)
    assert str(result) == "<button disabled></button>"


def test_boolean_attribute_false() -> None:
    result = button(disabled=False)
    assert str(result) == "<button></button>"
