from __future__ import annotations

import typing as t

import pytest

from htpy import Context, Node, div, fragment

if t.TYPE_CHECKING:
    from .conftest import RenderFixture

letter_ctx: Context[t.Literal["a", "b", "c"]] = Context("letter", default="a")
no_default_ctx: Context[str] = Context("no_default")


@letter_ctx.consumer
def display_letter(letter: t.Literal["a", "b", "c"], greeting: str) -> str:
    return f"{greeting}: {letter}!"


@no_default_ctx.consumer
def display_no_default(value: str) -> str:
    return f"{value=}"


def test_context_default(render: RenderFixture) -> None:
    result = div[display_letter("Yo")]
    assert render(result) == ["<div>", "Yo: a!", "</div>"]


def test_context_provider(render: RenderFixture) -> None:
    result = letter_ctx.provider("c", div[display_letter("Hello")])
    assert render(result) == ["<div>", "Hello: c!", "</div>"]


def test_no_default(render: RenderFixture) -> None:
    with pytest.raises(
        LookupError,
        match='Context value for "no_default" does not exist, requested by display_no_default()',
    ):
        render(div[display_no_default()])


def test_nested_override(render: RenderFixture) -> None:
    result = div[
        letter_ctx.provider(
            "b",
            letter_ctx.provider(
                "c",
                display_letter("Nested"),
            ),
        )
    ]
    assert render(result) == ["<div>", "Nested: c!", "</div>"]


def test_multiple_consumers(render: RenderFixture) -> None:
    a_ctx: Context[t.Literal["a"]] = Context("a_ctx", default="a")
    b_ctx: Context[t.Literal["b"]] = Context("b_ctx", default="b")

    @b_ctx.consumer
    @a_ctx.consumer
    def ab_display(a: t.Literal["a"], b: t.Literal["b"], greeting: str) -> str:
        return f"{greeting} a={a}, b={b}"

    result = div[ab_display("Hello")]
    assert render(result) == ["<div>", "Hello a=a, b=b", "</div>"]


def test_nested_consumer(render: RenderFixture) -> None:
    ctx: Context[str] = Context("ctx")

    @ctx.consumer
    def outer(value: str) -> Node:
        return inner(value)

    @ctx.consumer
    def inner(value: str, from_outer: str) -> Node:
        return f"outer: {from_outer}, inner: {value}"

    result = div[ctx.provider("foo", outer)]

    assert render(result) == ["<div>", "outer: foo, inner: foo", "</div>"]


def test_context_passed_via_iterable(render: RenderFixture) -> None:
    ctx: Context[str] = Context("ctx")

    @ctx.consumer
    def echo(value: str) -> str:
        return value

    result = div[ctx.provider("foo", [echo()])]

    assert render(result) == ["<div>", "foo", "</div>"]


def test_context_passed_via_fragment(render: RenderFixture) -> None:
    ctx: Context[str] = Context("ctx")

    @ctx.consumer
    def echo(value: str) -> str:
        return value

    result = div[ctx.provider("foo", fragment[echo()])]

    assert render(result) == ["<div>", "foo", "</div>"]
