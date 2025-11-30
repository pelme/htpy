from __future__ import annotations

import typing as t

import markupsafe

from htpy._render_async import aiter_chunks_node
from htpy._render_sync import chunks_as_markup, iter_chunks_node

try:
    from warnings import deprecated  # type: ignore[attr-defined,unused-ignore]
except ImportError:
    from typing_extensions import deprecated

if t.TYPE_CHECKING:
    from collections.abc import AsyncIterator, Iterator, Mapping

    from htpy._contexts import Context
    from htpy._types import Node


class Fragment:
    """A collection of nodes without a wrapping element."""

    __slots__ = ("_node",)

    def __init__(self) -> None:
        # Make it awkward to instantiate a Fragment directly:
        # Encourage using fragment[x]. That is why it is not possible to set the
        # node directly via the constructor.
        self._node: Node = None

    @deprecated(  # type: ignore[misc,unused-ignore]
        "iterating over a fragment is deprecated and will be removed in a future release. "
        "Please use the fragment.iter_chunks() method instead."
    )  # pyright: ignore [reportUntypedFunctionDecorator]
    def __iter__(self) -> Iterator[str]:
        return self.iter_chunks()

    def __str__(self) -> markupsafe.Markup:
        return chunks_as_markup(self)

    __html__ = __str__

    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        return iter_chunks_node(self._node, context)

    def aiter_chunks(
        self, context: Mapping[Context[t.Any], t.Any] | None = None
    ) -> AsyncIterator[str]:
        return aiter_chunks_node(self._node, context)

    @deprecated(
        "Calling .encode() on fragments is deprecated and will be removed in a future release. "
        "Using Starlette? Use htpy.starlette.HtpyResponse for improved performance and convenience. "  # noqa: E501
        "More info: https://htpy.dev/starlette/"
    )
    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)


class _FragmentGetter:
    def __getitem__(self, node: Node) -> Fragment:
        result = Fragment()
        result._node = node  # pyright: ignore[reportPrivateUsage]
        return result


fragment = _FragmentGetter()


def comment(text: str) -> Fragment:
    escaped_text = text.replace("--", "")
    return fragment[markupsafe.Markup(f"<!-- {escaped_text} -->")]
