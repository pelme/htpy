import pytest
from markupsafe import Markup
from typing_extensions import assert_type

import htpy
from htpy import Element, div


def test_instance_cache() -> None:
    """
    htpy creates element object dynamically. make sure they are reused.
    """
    assert htpy.div is htpy.div


def test_invalid_element_name() -> None:
    with pytest.raises(AttributeError, match="html elements must have all lowercase names"):
        htpy.Foo  # noqa: B018


def test_element_repr() -> None:
    assert repr(htpy.div("#a")) == """<Element '<div id="a"></div>'>"""


def test_void_element_repr() -> None:
    assert repr(htpy.hr("#a")) == """<VoidElement '<hr id="a">'>"""


def test_markup_str() -> None:
    result = str(div(id="a"))
    assert isinstance(result, str)
    assert isinstance(result, Markup)
    assert result == '<div id="a"></div>'


def test_element_type() -> None:
    assert_type(div, Element)
    assert isinstance(div, Element)

    assert_type(div(), Element)
    assert isinstance(div(), Element)

    assert_type(div()["a"], Element)
    assert isinstance(div()["a"], Element)
