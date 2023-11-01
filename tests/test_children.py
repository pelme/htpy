from typing import assert_type

import pytest

from htpy import Element, div, html, img, input, li, my_custom_element, ul


def test_void_element() -> None:
    element = input(name="foo")
    assert_type(element, Element)

    result = str(element)
    assert str(result) == '<input name="foo">'


def test_children() -> None:
    assert str(div[img]) == "<div><img></div>"


def test_multiple_children() -> None:
    result = ul[li, li]

    assert str(result) == "<ul><li></li><li></li></ul>"


def test_list_children() -> None:
    result = ul[[li["a"], li["b"]]]
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_tuple_children() -> None:
    result = ul[(li["a"], li["b"])]
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_generator_children() -> None:
    result = ul[(li[x] for x in ["a", "b"])]
    assert str(result) == "<ul><li>a</li><li>b</li></ul>"


def test_html_tag_with_doctype() -> None:
    result = html(foo="bar")["hello"]
    assert str(result) == '<!doctype html><html foo="bar">hello</html>'


def test_void_element_children() -> None:
    with pytest.raises(ValueError, match="img elements cannot have children"):
        img["hey"]


def test_call_without_args() -> None:
    result = img()
    assert str(result) == "<img>"


def test_custom_element() -> None:
    el = my_custom_element()
    assert_type(el, Element)
    assert str(el) == "<my-custom-element></my-custom-element>"


def test_ignore_none() -> None:
    assert str(div[None]) == "<div></div>"


def test_ignore_false() -> None:
    assert str(div[False]) == "<div></div>"


def test_do_not_ignore_zero() -> None:
    assert str(div[0]) == "<div>0</div>"
