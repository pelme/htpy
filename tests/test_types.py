from collections.abc import Generator
from typing import assert_type

from htpy import Element, RegularElement, VoidElement, div, img, li, ul


def test_element_type() -> None:
    assert_type(img, VoidElement)
    assert_type(div, RegularElement)
    assert_type(div(), RegularElement)
    assert_type(div()["a"], RegularElement)


def test_html_safestring_interface() -> None:
    result = str(div(id="a")).__html__()  # type: ignore[attr-defined]
    assert result == '<div id="a"></div>'


class Test_Children:
    def test_children_as_element(self) -> None:
        child: RegularElement = li
        ul[child]

    def test_children_as_list_element(self) -> None:
        child: list[Element] = [div]
        div[child]

    def test_children_as_generator_element(self) -> None:
        def gen() -> Generator[Element, None, None]:
            yield div

        div[gen()]
