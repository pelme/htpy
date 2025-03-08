from htpy import render_node, p, iter_node

from markupsafe import Markup


def test_render_node() -> None:
    result = render_node(p["hi"])
    assert isinstance(result, Markup)


def test_iter_node() -> None:
    result = list(iter_node(p["hi"]))
    assert result == ["<p>", "hi", "</p>"]


def test_element_iter() -> None:
    result = list(p["hi"])
    assert result == ["<p>", "hi", "</p>"]
