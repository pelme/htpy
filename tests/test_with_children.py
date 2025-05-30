from __future__ import annotations

import pytest

import htpy as h


@h.with_children
def example_with_children(
    content: h.Node,
    *,
    title: str = "default!",
) -> h.Renderable:
    return h.div[
        h.h1[title],
        h.p[content],
    ]


@pytest.mark.parametrize(
    ("component", "expected"),
    [
        (
            example_with_children,
            "with_children(example_with_children, <unbound>)",
        ),
        (
            example_with_children(title="title!"),
            "with_children(example_with_children, (), {'title': 'title!'})",
        ),
    ],
)
def test_with_children_repr(component: h.Renderable, expected: str) -> None:
    assert repr(component) == expected
