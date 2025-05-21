from __future__ import annotations

import typing as t

import pytest
from markupsafe import Markup

from htpy import button, div, th

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from .conftest import RenderFixture


def test_attribute(render: RenderFixture) -> None:
    assert render(div(id="hello")["hi"]) == ['<div id="hello">', "hi", "</div>"]


class Test_class_names:
    def test_str(self, render: RenderFixture) -> None:
        result = div(class_='">foo bar')
        assert render(result) == ['<div class="&#34;&gt;foo bar">', "</div>"]

    def test_safestring(self, render: RenderFixture) -> None:
        result = div(class_=Markup('">foo bar'))
        assert render(result) == ['<div class="&#34;&gt;foo bar">', "</div>"]

    def test_list(self, render: RenderFixture) -> None:
        result = div(class_=['">foo', Markup('">bar'), False, None, "", "baz"])
        assert render(result) == ['<div class="&#34;&gt;foo &#34;&gt;bar baz">', "</div>"]

    def test_tuple(self, render: RenderFixture) -> None:
        result = div(class_=('">foo', Markup('">bar'), False, None, "", "baz"))
        assert render(result) == ['<div class="&#34;&gt;foo &#34;&gt;bar baz">', "</div>"]

    def test_dict(self, render: RenderFixture) -> None:
        result = div(class_={'">foo': True, Markup('">bar'): True, "x": False, "baz": True})
        assert render(result) == ['<div class="&#34;&gt;foo &#34;&gt;bar baz">', "</div>"]

    def test_nested_dict(self, render: RenderFixture) -> None:
        result = div(
            class_=[
                '">list-foo',
                Markup('">list-bar'),
                {'">dict-foo': True, Markup('">list-bar'): True, "x": False},
            ]
        )
        assert render(result) == [
            '<div class="&#34;&gt;list-foo &#34;&gt;list-bar &#34;&gt;dict-foo &#34;&gt;list-bar">',
            "</div>",
        ]

    def test_false(self, render: RenderFixture) -> None:
        result = render(div(class_=False))
        assert result == ["<div>", "</div>"]

    def test_none(self, render: RenderFixture) -> None:
        result = render(div(class_=None))
        assert result == ["<div>", "</div>"]

    def test_no_classes(self, render: RenderFixture) -> None:
        result = render(div(class_={"foo": False}))
        assert result == ["<div>", "</div>"]


def test_dict_attributes(render: RenderFixture) -> None:
    result = div({"@click": 'hi = "hello"'})

    assert render(result) == ['<div @click="hi = &#34;hello&#34;">', "</div>"]


def test_dict_attributes_mapping(render: RenderFixture) -> None:
    attrs: Mapping[str, str] = {"id": "foo"}
    result = div(attrs)

    assert render(result) == ['<div id="foo">', "</div>"]


def test_underscore(render: RenderFixture) -> None:
    # Hyperscript (https://hyperscript.org/) uses _, make sure it works good.
    result = div(_="foo")
    assert render(result) == ['<div _="foo">', "</div>"]


def test_dict_attributes_avoid_replace(render: RenderFixture) -> None:
    result = div({"class_": "foo", "hello_hi": "abc"})
    assert render(result) == ['<div class_="foo" hello_hi="abc">', "</div>"]


def test_dict_attribute_false(render: RenderFixture) -> None:
    result = div({"bool-false": False})
    assert render(result) == ["<div>", "</div>"]


def test_dict_attribute_true(render: RenderFixture) -> None:
    result = div({"bool-true": True})
    assert render(result) == ["<div bool-true>", "</div>"]


def test_underscore_replacement(render: RenderFixture) -> None:
    result = button(hx_post="/foo")["click me!"]
    assert render(result) == ['<button hx-post="/foo">', "click me!", "</button>"]


class Test_attribute_escape:
    pytestmark = pytest.mark.parametrize(
        "x",
        [
            '<"foo',
            Markup('<"foo'),
        ],
    )

    def test_dict(self, x: str, render: RenderFixture) -> None:
        result = div({x: x})
        assert render(result) == ['<div &lt;&#34;foo="&lt;&#34;foo">', "</div>"]

    def test_kwarg(self, x: str, render: RenderFixture) -> None:
        result = div(**{x: x})
        assert render(result) == ['<div &lt;&#34;foo="&lt;&#34;foo">', "</div>"]


def test_boolean_attribute_true(render: RenderFixture) -> None:
    result = button(disabled=True)
    assert render(result) == ["<button disabled>", "</button>"]


def test_kwarg_attribute_none(render: RenderFixture) -> None:
    result = div(foo=None)
    assert render(result) == ["<div>", "</div>"]


def test_dict_attribute_none(render: RenderFixture) -> None:
    result = div({"foo": None})
    assert render(result) == ["<div>", "</div>"]


def test_boolean_attribute_false(render: RenderFixture) -> None:
    result = button(disabled=False)
    assert render(result) == ["<button>", "</button>"]


def test_integer_attribute(render: RenderFixture) -> None:
    result = th(colspan=123)
    assert render(result) == ['<th colspan="123">', "</th>"]


def test_id_class(render: RenderFixture) -> None:
    result = div("#myid.cls1.cls2")
    assert render(result) == ['<div id="myid" class="cls1 cls2">', "</div>"]


def test_id_class_only_id(render: RenderFixture) -> None:
    result = div("#myid")
    assert render(result) == ['<div id="myid">', "</div>"]


def test_id_class_only_classes(render: RenderFixture) -> None:
    result = div(".foo.bar")
    assert render(result) == ['<div class="foo bar">', "</div>"]


def test_id_class_spaces_only_id(render: RenderFixture) -> None:
    result = div("#a ")
    assert render(result) == ['<div id="a">', "</div>"]


def test_id_class_spaces_only_classes(render: RenderFixture) -> None:
    result = div(".a ")
    assert render(result) == ['<div class="a">', "</div>"]


def test_id_class_spaces(render: RenderFixture) -> None:
    result = div("#a .a ")
    assert render(result) == ['<div id="a" class="a">', "</div>"]


def test_id_class_wrong_order() -> None:
    with pytest.raises(ValueError, match="id \\(#\\) must be specified before classes \\(\\.\\)"):
        div(".myclass#myid")


def test_id_class_bad_format() -> None:
    with pytest.raises(ValueError, match="id/class strings must start with # or ."):
        div("foo")


def test_id_class_bad_type() -> None:
    with pytest.raises(TypeError, match="id/class strings must be str. got 3"):
        div(3, {})  # type: ignore


def test_id_class_and_kwargs(render: RenderFixture) -> None:
    result = div("#theid", for_="hello", data_foo="<bar")
    assert render(result) == ['<div id="theid" for="hello" data-foo="&lt;bar">', "</div>"]


def test_multiple_attrs(render: RenderFixture) -> None:
    result = div({"a": "1"}, {"a": "2", "b": "2"}, {"c": "3"})
    assert render(result) == ['<div a="2" b="2" c="3">', "</div>"]


def test_attrs_and_kwargs(render: RenderFixture) -> None:
    result = div({"a": "1", "for": "a"}, for_="b", b="2")
    assert render(result) == ['<div a="1" for="b" b="2">', "</div>"]


def test_class_priority_dict(render: RenderFixture) -> None:
    result = div(".a", {"class": "b"})
    assert render(result) == ['<div class="b">', "</div>"]


def test_class_priority_dict_and_kwarg(render: RenderFixture) -> None:
    result = div(".a", {"class": "b"}, class_="c")
    assert render(result) == ['<div class="c">', "</div>"]


def test_attribute_priority(render: RenderFixture) -> None:
    result = div({"foo": "a"}, foo="b")
    assert render(result) == ['<div foo="b">', "</div>"]


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
