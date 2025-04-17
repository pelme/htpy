from __future__ import annotations

import typing as t
from collections.abc import Iterable

import markupsafe

from htpy._types import (
    _HasHtml,  # pyright: ignore[reportPrivateUsage]
    _KnownInvalidChildren,  # pyright: ignore[reportPrivateUsage]
)

if t.TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from htpy._contexts import Context
    from htpy._types import Node, Renderable


def _chunks_as_markup(renderable: Renderable) -> markupsafe.Markup:  # pyright: ignore[reportUnusedFunction]
    return markupsafe.Markup("".join(renderable.iter_chunks()))


def _iter_chunks_node(x: Node, context: Mapping[Context[t.Any], t.Any] | None) -> Iterator[str]:
    from htpy._elements import BaseElement

    while not isinstance(x, BaseElement) and callable(x):
        x = x()

    if x is None:
        return

    if x is True:
        return

    if x is False:
        return

    if hasattr(x, "iter_chunks"):
        yield from x.iter_chunks(context)  # pyright: ignore
    elif isinstance(x, str | _HasHtml):
        yield str(markupsafe.escape(x))
    elif isinstance(x, int):
        yield str(x)
    elif isinstance(x, Iterable) and not isinstance(x, _KnownInvalidChildren):  # pyright: ignore [reportUnnecessaryIsInstance]
        for child in x:
            yield from _iter_chunks_node(child, context)
    else:
        raise TypeError(f"{x!r} is not a valid child element")
