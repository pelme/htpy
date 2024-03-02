import pytest

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


def test_id_class() -> None:
    result = div("#myid.cls1.cls2")

    assert str(result) == """<div id="myid" class="cls1 cls2"></div>"""


def test_id_class_only_id() -> None:
    result = div("#myid")
    assert str(result) == """<div id="myid"></div>"""


def test_id_class_only_classes() -> None:
    result = div(".foo.bar")
    assert str(result) == """<div class="foo bar"></div>"""


def test_id_class_wrong_order() -> None:
    with pytest.raises(ValueError, match="id \\(#\\) must be specified before classes \\(\\.\\)"):
        div(".myclass#myid")


def test_id_class_bad_format() -> None:
    with pytest.raises(ValueError, match="id/class strings must start with # or ."):
        div("foo")


def test_id_class_bad_type() -> None:
    with pytest.raises(ValueError, match="id/class strings must be str. got {'oops': 'yes'}"):
        div({"oops": "yes"}, {})  # type: ignore


def test_id_class_and_kwargs() -> None:
    result = div("#theid", for_="hello", data_foo="<bar")
    assert str(result) == """<div id="theid" for="hello" data-foo="&lt;bar"></div>"""


def test_attrs_and_kwargs() -> None:
    result = div({"a": "1", "for": "a"}, for_="b", b="2")
    assert str(result) == """<div a="1" for="b" b="2"></div>"""


def test_class_priority() -> None:
    result = div(".a", {"class": "b"}, class_="c")
    assert str(result) == """<div class="c"></div>"""

    result = div(".a", {"class": "b"})
    assert str(result) == """<div class="b"></div>"""


def test_attribute_priority() -> None:
    result = div({"foo": "a"}, foo="b")
    assert str(result) == """<div foo="b"></div>"""
