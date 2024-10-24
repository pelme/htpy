from __future__ import annotations

import typing as t

import pytest

from htpy import Element, li, ul

from .conftest import Trace

if t.TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from .conftest import RenderFixture, TraceFixture


def test_async_iterator(render_async: RenderFixture, trace: TraceFixture) -> None:
    async def lis() -> AsyncIterator[Element]:
        trace("pre a")
        yield li["a"]
        trace("pre b")
        yield li["b"]
        trace("post b")

    result = render_async(ul[lis()])
    assert result == [
        "<ul>",
        Trace("pre a"),
        "<li>",
        "a",
        "</li>",
        Trace("pre b"),
        "<li>",
        "b",
        "</li>",
        Trace("post b"),
        "</ul>",
    ]


def test_awaitable(render_async: RenderFixture, trace: TraceFixture) -> None:
    async def hi() -> Element:
        trace("in hi()")
        return li["hi"]

    result = render_async(ul[hi()])
    assert result == [
        "<ul>",
        Trace("in hi()"),
        "<li>",
        "hi",
        "</li>",
        "</ul>",
    ]


@pytest.mark.filterwarnings(r"ignore:coroutine '.*\.coroutine' was never awaited")
def test_sync_iteration_coroutine() -> None:
    async def coroutine() -> None:
        return None

    with pytest.raises(
        ValueError,
        match=(
            r"<coroutine object .+ at .+> is not a valid child element\. "
            r"Use async iteration to retrieve element content: https://htpy.dev/streaming/"
        ),
    ):
        list(ul[coroutine()])


def test_sync_iteration_async_generator() -> None:
    async def generator() -> AsyncIterator[None]:
        return
        yield

    with pytest.raises(
        ValueError,
        match=(
            r"<async_generator object .+ at .+> is not a valid child element\. "
            r"Use async iteration to retrieve element content: https://htpy.dev/streaming/"
        ),
    ):
        list(ul[generator()])
