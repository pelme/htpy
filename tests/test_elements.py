from typing import assert_type

import pytest

from htpy import Element, div, html, img, input, li, my_custom_element, ul


def test_element() -> None:
    element = div()
    assert_type(element, Element)


def test_void_element() -> None:
    element = input(name="foo")
    assert_type(element, Element)

    result = str(element)
    assert str(result) == '<input name="foo">'


def test_list_children() -> None:
    result = ul([li("a"), li("b")])
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_generator_children() -> None:
    result = ul(li(x) for x in ["a", "b"])
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_html_tag_with_doctype() -> None:
    result = html(foo="bar")("hello")
    assert str(result) == '<!doctype html><html foo="bar">hello</html>'


def test_void_element_children() -> None:
    with pytest.raises(ValueError, match="img elements cannot have children"):
        img("hey")


def test_call_without_args() -> None:
    result = img()
    assert str(result) == "<img>"


def test_custom_element() -> None:
    el = my_custom_element()
    assert_type(el, Element)
    assert str(el) == "<my-custom-element></my-custom-element>"
