from htpy import button, div


def test_class_str():
    result = div(class_=">foo bar")
    assert str(result) == '<div class="&gt;foo bar"></div>'


def test_class_list():
    result = div(class_=[">foo", False, None, "", "bar"])
    assert str(result) == '<div class="&gt;foo bar"></div>'


def test_class_dict():
    result = div(class_={">foo": True, "x": False, "y": None, "z": "", "bar": True})
    assert str(result) == '<div class="&gt;foo bar"></div>'


def test_dict_attributes():
    result = div({"@click": 'hi = "hello"'})("hello")

    assert str(result) == """<div @click="hi = &quot;hello&quot;">hello</div>"""


def test_underscore_replacement():
    result = button(hx_post="/foo")("click me!")
    assert str(result) == """<button hx-post="/foo">click me!</button>"""


def test_escape_attribute_name():
    result = div({"<disturbing attr>": "value"})
    assert str(result) == """<div &lt;disturbing attr&gt;="value"></div>"""


def test_boolean_attribute_true():
    result = button(disabled=True)("I am disabled")
    assert str(result) == "<button disabled>I am disabled</button>"


def test_boolean_attribute_false():
    result = button(disabled=False)("I am not disabled")
    assert str(result) == "<button>I am not disabled</button>"
