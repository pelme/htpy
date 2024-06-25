from typing import Any

from markupsafe import Markup

from htpy import div, iter_node, render_node, tr


def assert_markup(result: Any, expected: str) -> None:
    assert isinstance(result, Markup)
    assert result == expected


class Test_render_node:
    def test_element(self) -> None:
        result = render_node(div["a"])
        assert_markup(result, "<div>a</div>")

    def test_list(self) -> None:
        result = render_node([tr["a"], tr["b"]])

        assert_markup(result, "<tr>a</tr><tr>b</tr>")

    def test_none(self) -> None:
        result = render_node(None)
        assert_markup(result, "")

    def test_string(self) -> None:
        result = render_node("hej!")
        assert_markup(result, "hej!")


class Test_iter_node:
    def test_element(self) -> None:
        result = list(iter_node(div["a"]))

        # Ensure we get str back, not markup.
        assert type(result[0]) is str
        assert result == ["<div>", "a", "</div>"]

    def test_list(self) -> None:
        result = list(iter_node([tr["a"], tr["b"]]))
        assert result == ["<tr>", "a", "</tr>", "<tr>", "b", "</tr>"]

    def test_none(self) -> None:
        result = list(iter_node(None))
        assert result == []

    def test_string(self) -> None:
        result = list(iter_node("hej!"))
        assert result == ["hej!"]
