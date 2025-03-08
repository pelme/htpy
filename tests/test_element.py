import markupsafe
import pytest
from typing_extensions import assert_type

import htpy
from htpy import Element, break_, class_, del_, div, imaginary, imaginary_


def test_instance_cache() -> None:
    """
    htpy creates element object dynamically. make sure they are reused.
    """
    assert htpy.div is htpy.div


def test_invalid_element_name() -> None:
    with pytest.raises(AttributeError, match="html elements must have all lowercase names"):
        htpy.Foo  # noqa: B018


def test_element_repr() -> None:
    assert repr(htpy.div("#a")) == """<Element '<div id="a">...</div>'>"""


def test_void_element_repr() -> None:
    assert repr(htpy.hr("#a")) == """<VoidElement '<hr id="a">'>"""


def test_element_type() -> None:
    assert_type(div, Element)
    assert isinstance(div, Element)

    assert_type(div(), Element)
    assert isinstance(div(), Element)

    assert_type(div()["a"], Element)
    assert isinstance(div()["a"], Element)


def test_markupsafe_escape() -> None:
    result = markupsafe.escape(div["test"])
    assert result == "<div>test</div>"
    assert isinstance(result, markupsafe.Markup)


@pytest.mark.parametrize(
    ("element", "expected"),
    [(del_, "<del></del>"), (class_, "<class></class>"), (break_, "<break></break>")],
)
def test_keyword_named_elements(element: Element, expected: str) -> None:
    actual = str(element)
    assert actual == expected


@pytest.mark.parametrize(
    ("element", "expected"),
    [(imaginary, "<imaginary></imaginary>"), (imaginary_, "<imaginary-></imaginary->")],
)
def test_non_keyword_named_elements(element: Element, expected: str) -> None:
    actual = str(element)
    assert actual == expected
