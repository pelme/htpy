from __future__ import annotations

import typing as t
import weakref
from collections.abc import Generator, Iterable

import markupsafe

from htpy._types import HasHtml, KnownInvalidChildren

if t.TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    from htpy._contexts import Context
    from htpy._types import Node, Renderable

# Track consumed generators to prevent double consumption
_consumed_generators: weakref.WeakSet[Generator[t.Any, t.Any, t.Any]] = weakref.WeakSet()


def chunks_as_markup(renderable: Renderable) -> markupsafe.Markup:
    return markupsafe.Markup("".join(renderable.iter_chunks()))


def iter_chunks_node(x: Node, context: Mapping[Context[t.Any], t.Any] | None) -> Iterator[str]:
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
    elif isinstance(x, str | HasHtml):
        yield str(markupsafe.escape(x))
    elif isinstance(x, int):
        yield str(x)
    elif isinstance(x, Generator):
        if x in _consumed_generators:
            raise RuntimeError("Generator has already been consumed")
        _consumed_generators.add(x)
        for child in x:
            yield from iter_chunks_node(child, context)
    elif isinstance(x, Iterable) and not isinstance(x, KnownInvalidChildren):  # pyright: ignore [reportUnnecessaryIsInstance]
        for child in x:
            yield from iter_chunks_node(child, context)
    else:
        raise TypeError(f"{x!r} is not a valid child element")
