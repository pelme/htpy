from __future__ import annotations

import dataclasses
import functools
import typing as t

from htpy._rendering import chunks_as_markup, iter_chunks_node

try:
    from warnings import deprecated  # type: ignore[attr-defined,unused-ignore]
except ImportError:
    from typing_extensions import deprecated

if t.TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Mapping

    import markupsafe

    from htpy._types import Node


T = t.TypeVar("T")
P = t.ParamSpec("P")


@dataclasses.dataclass(frozen=True, slots=True)
class ContextProvider(t.Generic[T]):
    context: Context[T]
    value: T
    node: Node

    @deprecated(  # type: ignore[misc,unused-ignore]
        "iterating over a context provider is deprecated and will be removed in a future release. "
        "Please use the context_provider.iter_chunks() method instead."
    )  # pyright: ignore [reportUntypedFunctionDecorator]
    def __iter__(self) -> Iterator[str]:
        return self.iter_chunks()

    def __str__(self) -> markupsafe.Markup:
        return chunks_as_markup(self)

    __html__ = __str__

    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        return iter_chunks_node(self.node, {**(context or {}), self.context: self.value})  # pyright: ignore [reportUnknownMemberType]

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)


@dataclasses.dataclass(frozen=True, slots=True)
class ContextConsumer(t.Generic[T]):
    context: Context[T]
    debug_name: str
    func: Callable[[T], Node]

    def __str__(self) -> markupsafe.Markup:
        return chunks_as_markup(self)

    __html__ = __str__

    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        context_value = (context or {}).get(self.context, self.context.default)

        if context_value is _NO_DEFAULT:
            raise LookupError(
                f'Context value for "{self.context.name}" does not exist, '  # pyright: ignore
                f"requested by {self.debug_name}()."
            )
        return iter_chunks_node(self.func(context_value), context)  # pyright: ignore

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)


class _NO_DEFAULT:
    pass


@dataclasses.dataclass(frozen=True, slots=True)
class Context(t.Generic[T]):
    name: str
    _: dataclasses.KW_ONLY
    default: T | type[_NO_DEFAULT] = _NO_DEFAULT

    def provider(self, value: T, node: Node) -> ContextProvider[T]:
        return ContextProvider(self, value, node)

    def consumer(
        self,
        func: Callable[t.Concatenate[T, P], Node],
    ) -> Callable[P, ContextConsumer[T]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> ContextConsumer[T]:
            return ContextConsumer(self, func.__name__, lambda value: func(value, *args, **kwargs))

        return wrapper
