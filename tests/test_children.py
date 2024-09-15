from __future__ import annotations

import dataclasses
import datetime
import decimal
import pathlib
import re
import typing as t

import pytest
from markupsafe import Markup
from typing_extensions import assert_type

from htpy import Element, VoidElement, dd, div, dl, dt, html, img, input, li, my_custom_element, ul

from .conftest import Trace

if t.TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from htpy import Node

    from .conftest import RenderFixture, TraceFixture


def test_void_element(render: RenderFixture) -> None:
    result = input(name="foo")
    assert_type(result, VoidElement)
    assert isinstance(result, VoidElement)

    assert render(result) == ['<input name="foo">']


def test_integer_child(render: RenderFixture) -> None:
    assert render(div[123]) == ["<div>", "123", "</div>"]


def test_children(render: RenderFixture) -> None:
    assert render(div[img]) == ["<div>", "<img>", "</div>"]


def test_multiple_children(render: RenderFixture) -> None:
    result = ul[li, li]

    assert render(result) == ["<ul>", "<li>", "</li>", "<li>", "</li>", "</ul>"]


def test_list_children(render: RenderFixture) -> None:
    children: list[Element] = [li["a"], li["b"]]
    result = ul[children]
    assert render(result) == ["<ul>", "<li>", "a", "</li>", "<li>", "b", "</li>", "</ul>"]


def test_tuple_children(render: RenderFixture) -> None:
    result = ul[(li["a"], li["b"])]
    assert render(result) == ["<ul>", "<li>", "a", "</li>", "<li>", "b", "</li>", "</ul>"]


def test_flatten_nested_children(render: RenderFixture) -> None:
    result = dl[
        [
            (dt["a"], dd["b"]),
            (dt["c"], dd["d"]),
        ]
    ]
    assert render(result) == [
        "<dl>",
        "<dt>",
        "a",
        "</dt>",
        "<dd>",
        "b",
        "</dd>",
        "<dt>",
        "c",
        "</dt>",
        "<dd>",
        "d",
        "</dd>",
        "</dl>",
    ]


def test_flatten_very_nested_children(render: RenderFixture) -> None:
    # maybe not super useful but the nesting may be arbitrarily deep
    result = div[[([["a"]],)], [([["b"]],)]]
    assert render(result) == ["<div>", "a", "b", "</div>"]


def test_flatten_nested_generators(render: RenderFixture) -> None:
    def cols() -> Generator[str, None, None]:
        yield "a"
        yield "b"
        yield "c"

    def rows() -> Generator[Generator[str, None, None], None, None]:
        yield cols()
        yield cols()
        yield cols()

    result = div[rows()]

    assert render(result) == ["<div>", "a", "b", "c", "a", "b", "c", "a", "b", "c", "</div>"]


def test_generator_children(render: RenderFixture) -> None:
    gen: Generator[Element, None, None] = (li[x] for x in ["a", "b"])
    result = ul[gen]
    assert render(result) == ["<ul>", "<li>", "a", "</li>", "<li>", "b", "</li>", "</ul>"]


def test_html_tag_with_doctype(render: RenderFixture) -> None:
    result = html(foo="bar")["hello"]
    assert render(result) == ["<!doctype html>", '<html foo="bar">', "hello", "</html>"]


def test_void_element_children() -> None:
    with pytest.raises(TypeError):
        img["hey"]  # type: ignore[index]


def test_call_without_args(render: RenderFixture) -> None:
    result = img()
    assert render(result) == ["<img>"]


def test_custom_element(render: RenderFixture) -> None:
    result = my_custom_element()
    assert_type(result, Element)
    assert isinstance(result, Element)
    assert render(result) == ["<my-custom-element>", "</my-custom-element>"]


@pytest.mark.parametrize("ignored_value", [None, True, False])
def test_ignored(render: RenderFixture, ignored_value: t.Any) -> None:
    assert render(div[ignored_value]) == ["<div>", "</div>"]


def test_lazy_iter(render: RenderFixture, trace: TraceFixture) -> None:
    def generate_list() -> Generator[Element, None, None]:
        trace("before yield")
        yield li("#a")
        trace("after yield")

    result = render(ul[generate_list()])
    assert result == [
        "<ul>",
        Trace("before yield"),
        '<li id="a">',
        "</li>",
        Trace("after yield"),
        "</ul>",
    ]


def test_lazy_callable(render: RenderFixture, trace: TraceFixture) -> None:
    def parent() -> Element:
        trace("in parent")
        return div("#parent")[child]

    def child() -> str:
        trace("in child")
        return "child"

    result = render(div[parent])

    assert result == [
        "<div>",
        Trace(description="in parent"),
        '<div id="parent">',
        Trace(description="in child"),
        "child",
        "</div>",
        "</div>",
    ]


def test_iter_str(render: RenderFixture) -> None:
    _, child, _ = render(div["a"])

    assert child == "a"
    # Make sure we dont get Markup (subclass of str)
    assert type(child) is str


def test_iter_markup(render: RenderFixture) -> None:
    _, child, _ = render(div["a"])

    assert child == "a"
    # Make sure we dont get Markup (subclass of str)
    assert type(child) is str


def test_escape_children(render: RenderFixture) -> None:
    result = render(div['>"'])
    assert result == ["<div>", "&gt;&#34;", "</div>"]


def test_safe_children(render: RenderFixture) -> None:
    result = render(div[Markup("<hello></hello>")])
    assert result == ["<div>", "<hello></hello>", "</div>"]


def test_nested_callable_generator(render: RenderFixture) -> None:
    def func() -> Generator[str, None, None]:
        return (x for x in "abc")

    assert render(div[func]) == ["<div>", "a", "b", "c", "</div>"]


def test_nested_callables(render: RenderFixture) -> None:
    def first() -> Callable[[], Node]:
        return second

    def second() -> Node:
        return "hi"

    assert render(div[first]) == ["<div>", "hi", "</div>"]


def test_callable_in_generator(render: RenderFixture) -> None:
    assert render(div[((lambda: "hi") for _ in range(1))]) == ["<div>", "hi", "</div>"]


@dataclasses.dataclass
class MyDataClass:
    name: str


class SomeClass:
    pass


# Various types that are not valid children.
_invalid_children = [
    12.34,
    decimal.Decimal("12.34"),
    complex("+1.23"),
    object(),
    datetime.date(1, 2, 3),
    datetime.datetime(1, 2, 3),
    datetime.time(1, 2),
    b"foo",
    bytearray(b"foo"),
    memoryview(b"foo"),
    Exception("foo"),
    Ellipsis,
    re.compile("foo"),
    pathlib.Path("FOO"),
    re,  # module type
    MyDataClass(name="Andreas"),
    SomeClass(),
]


@pytest.mark.parametrize("not_a_child", _invalid_children)
def test_invalid_child_direct(not_a_child: t.Any) -> None:
    with pytest.raises(TypeError, match="is not a valid child element"):
        div[not_a_child]


@pytest.mark.parametrize("not_a_child", _invalid_children)
def test_invalid_child_nested_iterable(not_a_child: t.Any) -> None:
    with pytest.raises(TypeError, match="is not a valid child element"):
        div[[not_a_child]]


@pytest.mark.parametrize("not_a_child", _invalid_children)
def test_invalid_child_lazy_callable(not_a_child: t.Any, render: RenderFixture) -> None:
    """
    Ensure proper exception is raised for lazily evaluated invalid children.
    """
    element = div[lambda: not_a_child]
    with pytest.raises(TypeError, match="is not a valid child element"):
        render(element)


@pytest.mark.parametrize("not_a_child", _invalid_children)
def test_invalid_child_lazy_generator(not_a_child: t.Any, render: RenderFixture) -> None:
    """
    Ensure proper exception is raised for lazily evaluated invalid children.
    """

    def gen() -> t.Any:
        yield not_a_child

    element = div[gen()]
    with pytest.raises(TypeError, match="is not a valid child element"):
        render(element)
