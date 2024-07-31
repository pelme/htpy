from collections.abc import AsyncIterator

import pytest

from htpy import Element, li, ul


async def async_lis() -> AsyncIterator[Element]:
    yield li["a"]
    yield li["b"]


async def hi() -> Element:
    return li["hi"]


@pytest.mark.asyncio
async def test_async_iterator() -> None:
    result = [chunk async for chunk in ul[async_lis()]]
    assert result == ["<ul>", "<li>", "a", "</li>", "<li>", "b", "</li>", "</ul>"]


@pytest.mark.asyncio
async def test_cororoutinefunction_children() -> None:
    result = [chunk async for chunk in ul[hi]]
    assert result == ["<ul>", "<li>", "hi", "</li>", "</ul>"]


@pytest.mark.asyncio
async def test_cororoutine_children() -> None:
    result = [chunk async for chunk in ul[hi()]]
    assert result == ["<ul>", "<li>", "hi", "</li>", "</ul>"]


def test_sync_iteration_with_async_children() -> None:
    with pytest.raises(
        ValueError,
        match="<async_generator object async_lis at .+> is not a valid child element",
    ):
        str(ul[async_lis()])
