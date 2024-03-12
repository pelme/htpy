from collections.abc import Generator

from htpy import Element, VoidElement, br, div, li, ul


def test_generator() -> None:
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


def test_callable() -> None:
    called = False

    def generate_br() -> VoidElement:
        nonlocal called
        called = True
        return br

    iterator = iter(div[generate_br])

    assert next(iterator) == "<div>"
    assert called is False
    assert next(iterator) == "<br>"
    assert called is True
    assert next(iterator) == "</div>"
