from __future__ import annotations

from typing import TYPE_CHECKING, Any

import pytest
from markupsafe import Markup
from typing_extensions import assert_type

from htpy import Element, VoidElement, dd, div, dl, dt, html, img, input, li, my_custom_element, ul

if TYPE_CHECKING:
    from collections.abc import Callable, Generator

    from htpy import Node


def test_void_element() -> None:
    element = input(name="foo")
    assert_type(element, VoidElement)
    assert isinstance(element, VoidElement)

    result = str(element)
    assert str(result) == '<input name="foo">'


def test_children() -> None:
    assert str(div[img]) == "<div><img></div>"


def test_multiple_children() -> None:
    result = ul[li, li]

    assert str(result) == "<ul><li></li><li></li></ul>"


def test_list_children() -> None:
    children: list[Element] = [li["a"], li["b"]]
    result = ul[children]
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_tuple_children() -> None:
    result = ul[(li["a"], li["b"])]
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_flatten_nested_children() -> None:
    result = dl[
        [
            (dt["a"], dd["b"]),
            (dt["c"], dd["d"]),
        ]
    ]
    assert str(result) == """<dl><dt>a</dt><dd>b</dd><dt>c</dt><dd>d</dd></dl>"""


def test_flatten_very_nested_children() -> None:
    # maybe not super useful but the nesting may be arbitrarily deep
    result = div[[([["a"]],)], [([["b"]],)]]
    assert str(result) == """<div>ab</div>"""


def test_flatten_nested_generators() -> None:
    def cols() -> Generator[str, None, None]:
        yield "a"
        yield "b"
        yield "c"

    def rows() -> Generator[Generator[str, None, None], None, None]:
        yield cols()
        yield cols()
        yield cols()

    result = div[rows()]

    assert str(result) == """<div>abcabcabc</div>"""


def test_generator_children() -> None:
    gen: Generator[Element, None, None] = (li[x] for x in ["a", "b"])
    result = ul[gen]
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_html_tag_with_doctype() -> None:
    result = html(foo="bar")["hello"]
    assert str(result) == '<!doctype html><html foo="bar">hello</html>'


def test_void_element_children() -> None:
    with pytest.raises(TypeError):
        img["hey"]  # type: ignore[index]


def test_call_without_args() -> None:
    result = img()
    assert str(result) == "<img>"


def test_custom_element() -> None:
    el = my_custom_element()
    assert_type(el, Element)
    assert isinstance(el, Element)
    assert str(el) == "<my-custom-element></my-custom-element>"


def test_ignore_none() -> None:
    assert str(div[None]) == "<div></div>"


def test_iter() -> None:
    trace = "not started"

    def generate_list() -> Generator[Element, None, None]:
        nonlocal trace

        trace = "before yield"
        yield li("#a")

        trace = "done"

    iterator = iter(ul[generate_list()])

    assert next(iterator) == "<ul>"
    assert trace == "not started"

    assert next(iterator) == '<li id="a">'
    assert trace == "before yield"
    assert next(iterator) == "</li>"
    assert trace == "before yield"

    assert next(iterator) == "</ul>"
    assert trace == "done"


def test_iter_str() -> None:
    _, child, _ = div["a"]

    assert child == "a"
    # Make sure we dont get Markup (subclass of str)
    assert type(child) is str  # noqa


def test_iter_markup() -> None:
    _, child, _ = div["a"]

    assert child == "a"
    # Make sure we dont get Markup (subclass of str)
    assert type(child) is str  # noqa


def test_callable() -> None:
    called = False

    def generate_img() -> VoidElement:
        nonlocal called
        called = True
        return img

    iterator = iter(div[generate_img])

    assert next(iterator) == "<div>"
    assert called is False
    assert next(iterator) == "<img>"
    assert called is True
    assert next(iterator) == "</div>"


def test_escape_children() -> None:
    result = str(div['>"'])
    assert result == "<div>&gt;&#34;</div>"


def test_safe_children() -> None:
    result = str(div[Markup("<hello></hello>")])
    assert result == "<div><hello></hello></div>"


def test_nested_callable_generator() -> None:
    def func() -> Generator[str, None, None]:
        return (x for x in "abc")

    assert str(div[func]) == "<div>abc</div>"


def test_nested_callables() -> None:
    def first() -> Callable[[], Node]:
        return second

    def second() -> Node:
        return "hi"

    assert str(div[first]) == "<div>hi</div>"


def test_callable_in_generator() -> None:
    assert str(div[((lambda: "hi") for _ in range(1))]) == "<div>hi</div>"


@pytest.mark.parametrize("not_a_child", [1234, True, False, b"foo", object(), object])
def test_invalid_child(not_a_child: Any) -> None:
    with pytest.raises(ValueError, match="is not a valid child element"):
        str(div[not_a_child])
