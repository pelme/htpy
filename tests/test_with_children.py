from __future__ import annotations

import pytest

import htpy as h


@h.with_children
def my_component(
    content: h.Node,
    *,
    title: str = "Default title",
) -> h.Element:
    return h.div[
        h.h1[title],
        h.p[content],
    ]


@pytest.mark.parametrize(
    ("component", "expected"),
    [
        (
            my_component,
            "with_children(my_component, <unbound>)",
        ),
        (
            my_component(title="My title"),
            "with_children(my_component, (), {'title': 'My title'})",
        ),
    ],
)
def test_with_children_repr(component: h.Renderable, expected: str) -> None:
    assert repr(component) == expected


@pytest.mark.parametrize(
    ("component", "expected"),
    [
        (
            my_component,
            "<div><h1>Default title</h1><p></p></div>",
        ),
        (
            my_component["My ", "content"],
            "<div><h1>Default title</h1><p>My content</p></div>",
        ),
        (
            my_component(title="My title"),
            "<div><h1>My title</h1><p></p></div>",
        ),
        (
            my_component(title="My title")["My ", "content"],
            "<div><h1>My title</h1><p>My content</p></div>",
        ),
    ],
)
def test_with_children_str(component: h.Renderable, expected: str) -> None:
    assert str(component) == expected


@pytest.mark.parametrize(
    ("component", "expected"),
    [
        (
            my_component,
            "<div><h1>Default title</h1><p></p></div>",
        ),
        (
            my_component["My ", "content"],
            "<div><h1>Default title</h1><p>My content</p></div>",
        ),
        (
            my_component(title="My title"),
            "<div><h1>My title</h1><p></p></div>",
        ),
        (
            my_component(title="My title")["My ", "content"],
            "<div><h1>My title</h1><p>My content</p></div>",
        ),
    ],
)
def test_with_children_html(component: h.Renderable, expected: str) -> None:
    assert component.__html__() == expected


@pytest.mark.parametrize(
    ("component", "expected"),
    [
        (
            my_component,
            b"<div><h1>Default title</h1><p></p></div>",
        ),
        (
            my_component["My ", "content"],
            b"<div><h1>Default title</h1><p>My content</p></div>",
        ),
        (
            my_component(title="My title"),
            b"<div><h1>My title</h1><p></p></div>",
        ),
        (
            my_component(title="My title")["My ", "content"],
            b"<div><h1>My title</h1><p>My content</p></div>",
        ),
    ],
)
def test_with_children_encode(component: h.Renderable, expected: bytes) -> None:
    assert component.encode() == expected


@pytest.mark.parametrize(
    ("component", "expected"),
    [
        (
            my_component,
            ["<div>", "<h1>", "Default title", "</h1>", "<p>", "</p>", "</div>"],
        ),
        (
            my_component["My ", "content"],
            [
                "<div>",
                "<h1>",
                "Default title",
                "</h1>",
                "<p>",
                "My ",
                "content",
                "</p>",
                "</div>",
            ],
        ),
        (
            my_component(title="My title"),
            ["<div>", "<h1>", "My title", "</h1>", "<p>", "</p>", "</div>"],
        ),
        (
            my_component(title="My title")["My ", "content"],
            [
                "<div>",
                "<h1>",
                "My title",
                "</h1>",
                "<p>",
                "My ",
                "content",
                "</p>",
                "</div>",
            ],
        ),
    ],
)
def test_with_children_iter_chunks(component: h.Renderable, expected: list[str]) -> None:
    assert list(component.iter_chunks()) == expected
