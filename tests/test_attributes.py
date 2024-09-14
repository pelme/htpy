import typing as t

import pytest
from markupsafe import Markup

from htpy import button, div, th


def test_attribute() -> None:
    assert str(div(id="hello")["hi"]) == '<div id="hello">hi</div>'


class Test_class_names:
    def test_str(self) -> None:
        result = div(class_='">foo bar')
        assert str(result) == '<div class="&#34;&gt;foo bar"></div>'

    def test_safestring(self) -> None:
        result = div(class_=Markup('">foo bar'))
        assert str(result) == '<div class="&#34;&gt;foo bar"></div>'

    def test_list(self) -> None:
        result = div(class_=['">foo', Markup('">bar'), False, None, "", "baz"])
        assert str(result) == '<div class="&#34;&gt;foo &#34;&gt;bar baz"></div>'

    def test_tuple(self) -> None:
        result = div(class_=('">foo', Markup('">bar'), False, None, "", "baz"))
        assert str(result) == '<div class="&#34;&gt;foo &#34;&gt;bar baz"></div>'

    def test_dict(self) -> None:
        result = div(class_={'">foo': True, Markup('">bar'): True, "x": False, "baz": True})
        assert str(result) == '<div class="&#34;&gt;foo &#34;&gt;bar baz"></div>'

    def test_nested_dict(self) -> None:
        result = div(
            class_=[
                '">list-foo',
                Markup('">list-bar'),
                {'">dict-foo': True, Markup('">list-bar'): True, "x": False},
            ]
        )
        assert str(result) == (
            '<div class="&#34;&gt;list-foo &#34;&gt;list-bar '
            '&#34;&gt;dict-foo &#34;&gt;list-bar"></div>'
        )

    def test_false(self) -> None:
        result = str(div(class_=False))
        assert result == "<div></div>"

    def test_none(self) -> None:
        result = str(div(class_=None))
        assert result == "<div></div>"

    def test_no_classes(self) -> None:
        result = str(div(class_={"foo": False}))
        assert result == "<div></div>"


def test_dict_attributes() -> None:
    result = div({"@click": 'hi = "hello"'})

    assert str(result) == """<div @click="hi = &#34;hello&#34;"></div>"""


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


class Test_attribute_escape:
    pytestmark = pytest.mark.parametrize(
        "x",
        [
            '<"foo',
            Markup('<"foo'),
        ],
    )

    def test_dict(self, x: str) -> None:
        result = div({x: x})
        assert str(result) == """<div &lt;&#34;foo="&lt;&#34;foo"></div>"""

    def test_kwarg(self, x: str) -> None:
        result = div(**{x: x})
        assert str(result) == """<div &lt;&#34;foo="&lt;&#34;foo"></div>"""


def test_boolean_attribute_true() -> None:
    result = button(disabled=True)
    assert str(result) == "<button disabled></button>"


def test_kwarg_attribute_none() -> None:
    result = div(foo=None)
    assert str(result) == "<div></div>"


def test_dict_attribute_none() -> None:
    result = div({"foo": None})
    assert str(result) == "<div></div>"


def test_boolean_attribute_false() -> None:
    result = button(disabled=False)
    assert str(result) == "<button></button>"


def test_integer_attribute() -> None:
    result = th(colspan=123)
    assert str(result) == '<th colspan="123"></th>'


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
    with pytest.raises(TypeError, match="id/class strings must be str. got {'oops': 'yes'}"):
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


@pytest.mark.parametrize("not_an_attr", [1234, b"foo", object(), object, 1, 0, None])
def test_invalid_attribute_key(not_an_attr: t.Any) -> None:
    with pytest.raises(TypeError, match="Attribute key must be a string"):
        div({not_an_attr: "foo"})


@pytest.mark.parametrize(
    "not_an_attr",
    [12.34, b"foo", object(), object],
)
def test_invalid_attribute_value(not_an_attr: t.Any) -> None:
    with pytest.raises(TypeError, match="Attribute value must be a string"):
        div(foo=not_an_attr)
