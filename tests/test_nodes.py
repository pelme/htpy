from __future__ import annotations

import typing as t

from markupsafe import Markup

from htpy import div, render_node, tr

if t.TYPE_CHECKING:
    from .conftest import RenderFixture


def test_render_node_element() -> None:
    result = render_node(div["a"])
    assert result == "<div>a</div>"
    assert isinstance(result, Markup)


class Test_node_iteration:
    def test_element(self, render: RenderFixture) -> None:
        result = render(div["a"])

        # Ensure we get str back, not markup.
        assert type(result[0]) is str
        assert result == ["<div>", "a", "</div>"]

    def test_list(self, render: RenderFixture) -> None:
        result = render([tr["a"], tr["b"]])
        assert result == ["<tr>", "a", "</tr>", "<tr>", "b", "</tr>"]

    def test_none(self, render: RenderFixture) -> None:
        result = render(None)
        assert result == []

    def test_string(self, render: RenderFixture) -> None:
        result = render("hej!")
        assert result == ["hej!"]
