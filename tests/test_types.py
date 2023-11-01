from typing import assert_type

from htpy import Element, div


def test_element_type() -> None:
    assert_type(div, Element)
    assert_type(div(), Element)
    assert_type(div()["a"], Element)


def test_html_safestring_interface() -> None:
    result = div(id="a").__html__()
    assert_type(result, str)
    assert result == '<div id="a"></div>'
