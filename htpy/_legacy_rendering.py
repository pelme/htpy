from __future__ import annotations

import typing as t

import markupsafe

from htpy._fragments import fragment

try:
    from warnings import deprecated  # type: ignore[attr-defined,unused-ignore]
except ImportError:
    from typing_extensions import deprecated

if t.TYPE_CHECKING:
    from collections.abc import Iterator

    from htpy._types import Node


@deprecated(  # type: ignore[misc,unused-ignore]
    "iter_node is deprecated and will be removed in a future release. "
    "Please use the .iter_chunks() method on elements/fragments instead."
)  # pyright: ignore [reportUntypedFunctionDecorator]
def iter_node(x: Node) -> Iterator[str]:
    return fragment[x].iter_chunks()


@deprecated(  # type: ignore[misc,unused-ignore]
    "render_node is deprecated and will be removed in a future release. "
    "Please use fragment instead: https://htpy.dev/usage/#fragments"
)  # pyright: ignore [reportUntypedFunctionDecorator]
def render_node(node: Node) -> markupsafe.Markup:
    return markupsafe.Markup(fragment[node])
