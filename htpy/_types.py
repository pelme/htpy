from __future__ import annotations

import typing as t
from collections.abc import Callable, Iterable

if t.TYPE_CHECKING:
    from collections.abc import Iterator, Mapping

    import markupsafe

    from htpy._contexts import Context


@t.runtime_checkable
class HasHtml(t.Protocol):
    def __html__(self) -> str: ...


class Renderable(t.Protocol):
    def __str__(self) -> markupsafe.Markup: ...
    def __html__(self) -> markupsafe.Markup: ...
    def iter_chunks(
        self, context: Mapping[Context[t.Any], t.Any] | None = None
    ) -> Iterator[str]: ...

    # Allow starlette Response.render to directly render this element without
    # explicitly casting to str:
    # https://github.com/encode/starlette/blob/5ed55c441126687106109a3f5e051176f88cd3e6/starlette/responses.py#L44-L49
    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes: ...


_ClassNamesDict: t.TypeAlias = dict[str, bool]
_ClassNames: t.TypeAlias = Iterable[str | None | bool | _ClassNamesDict] | _ClassNamesDict
Attribute: t.TypeAlias = None | bool | str | int | HasHtml | _ClassNames

Node: t.TypeAlias = (
    Renderable | None | bool | str | int | HasHtml | Iterable["Node"] | Callable[[], "Node"]
)

KnownInvalidChildren: t.TypeAlias = bytes | bytearray | memoryview
