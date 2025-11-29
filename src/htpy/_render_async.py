from __future__ import annotations

import typing as t
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Iterable,
    Mapping,
)

import markupsafe

from ._types import HasHtml, KnownInvalidChildren, Node

if t.TYPE_CHECKING:
    from ._contexts import Context


async def aiter_chunks_node(
    x: Node, context: Mapping[Context[t.Any], t.Any] | None
) -> AsyncIterator[str]:
    from ._elements import BaseElement

    while True:
        if isinstance(x, Awaitable):
            x = await x  # pyright: ignore [reportUnknownVariableType]
            continue

        if not isinstance(x, BaseElement) and callable(x):  # pyright: ignore [reportUnknownArgumentType]
            x = x()  # pyright: ignore [reportAssignmentType]
            continue

        break

    if x is None:
        return

    if x is True:
        return

    if x is False:
        return

    if hasattr(x, "aiter_chunks"):  # pyright: ignore [reportUnknownVariableType, reportUnknownArgumentType]
        async for chunk in x.aiter_chunks(context):  # pyright: ignore
            yield chunk
    elif isinstance(x, str | HasHtml):
        yield str(markupsafe.escape(x))
    elif isinstance(x, int):
        yield str(x)
    elif isinstance(x, Iterable) and not isinstance(x, KnownInvalidChildren):  # pyright: ignore [reportUnnecessaryIsInstance]
        for child in x:  # pyright: ignore
            async for chunk in aiter_chunks_node(child, context):  # pyright: ignore
                yield chunk
    elif isinstance(x, AsyncIterable):  # pyright: ignore[reportUnnecessaryIsInstance]
        async for child in x:  # pyright: ignore[reportUnknownVariableType]
            async for chunk in aiter_chunks_node(child, context):  # pyright: ignore[reportUnknownArgumentType]
                yield chunk
    else:
        raise TypeError(f"{x!r} is not a valid child element")
