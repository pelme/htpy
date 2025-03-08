import pytest
from markupsafe import Markup

from htpy import fragment, iter_node, p, render_node  # pyright: ignore [reportDeprecated]


def test_render_node() -> None:
    with pytest.deprecated_call():
        result = render_node(p["hi"])  # pyright: ignore [reportDeprecated]
    assert isinstance(result, Markup)


def test_iter_node() -> None:
    with pytest.deprecated_call():
        result = list(iter_node(p["hi"]))  # pyright: ignore [reportDeprecated]
    assert result == ["<p>", "hi", "</p>"]


def test_element_iter() -> None:
    with pytest.deprecated_call():
        result = list(p["hi"])
    assert result == ["<p>", "hi", "</p>"]


def test_fragment_iter() -> None:
    with pytest.deprecated_call():
        assert list(fragment["foo"]) == ["foo"]
