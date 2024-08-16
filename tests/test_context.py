import typing as t

import pytest

from htpy import Context, Node, div

letter_ctx: Context[t.Literal["a", "b", "c"]] = Context("letter", default="a")
no_default_ctx = Context[str]("no_default")


@letter_ctx.consumer
def display_letter(letter: t.Literal["a", "b", "c"], greeting: str) -> str:
    return f"{greeting}: {letter}!"


@no_default_ctx.consumer
def display_no_default(value: str) -> str:
    return f"{value=}"


def test_context_default() -> None:
    result = div[display_letter("Yo")]
    assert str(result) == "<div>Yo: a!</div>"


def test_context_provider() -> None:
    result = letter_ctx.provider("c", lambda: div[display_letter("Hello")])
    assert str(result) == "<div>Hello: c!</div>"


def test_no_default() -> None:
    with pytest.raises(
        LookupError,
        match='Context value for "no_default" does not exist, requested by display_no_default()',
    ):
        str(div[display_no_default()])


def test_nested_override() -> None:
    result = div[
        letter_ctx.provider(
            "b",
            lambda: letter_ctx.provider(
                "c",
                lambda: display_letter("Nested"),
            ),
        )
    ]
    assert str(result) == "<div>Nested: c!</div>"


def test_multiple_consumers() -> None:
    a_ctx: Context[t.Literal["a"]] = Context("a_ctx", default="a")
    b_ctx: Context[t.Literal["b"]] = Context("b_ctx", default="b")

    @b_ctx.consumer
    @a_ctx.consumer
    def ab_display(a: t.Literal["a"], b: t.Literal["b"], greeting: str) -> str:
        return f"{greeting} a={a}, b={b}"

    result = div[ab_display("Hello")]
    assert str(result) == "<div>Hello a=a, b=b</div>"


def test_nested_consumer() -> None:
    ctx: Context[str] = Context("ctx")

    @ctx.consumer
    def outer(value: str) -> Node:
        return inner(value)

    @ctx.consumer
    def inner(value: str, from_outer: str) -> Node:
        return f"outer: {from_outer}, inner: {value}"

    result = div[ctx.provider("foo", outer)]

    assert str(result) == "<div>outer: foo, inner: foo</div>"


def test_context_passed_via_iterable() -> None:
    ctx: Context[str] = Context("ctx")

    @ctx.consumer
    def echo(value: str) -> str:
        return value

    result = div[ctx.provider("foo", lambda: [echo()])]

    assert str(result) == "<div>foo</div>"
