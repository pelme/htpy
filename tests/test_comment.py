from __future__ import annotations

import typing as t

from htpy import comment, div

if t.TYPE_CHECKING:
    from .conftest import RenderFixture


def test_simple(render: RenderFixture) -> None:
    assert render(div[comment("hi")]) == ["<div>", "<!-- hi -->", "</div>"]


def test_escape_two_dashes(render: RenderFixture) -> None:
    assert render(div[comment("foo--bar")]) == ["<div>", "<!-- foobar -->", "</div>"]


def test_escape_three_dashes(render: RenderFixture) -> None:
    assert render(div[comment("foo---bar")]) == ["<div>", "<!-- foo-bar -->", "</div>"]


def test_escape_four_dashes(render: RenderFixture) -> None:
    assert render(div[comment("foo----bar")]) == ["<div>", "<!-- foobar -->", "</div>"]
