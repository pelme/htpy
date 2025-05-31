from __future__ import annotations

import functools
import typing as t

import markupsafe

if t.TYPE_CHECKING:
    from collections.abc import Callable, Iterator, Mapping

    import htpy


C = t.TypeVar("C", bound="htpy.Node")
P = t.ParamSpec("P")
R = t.TypeVar("R", bound="htpy.Renderable")


class _WithChildrenUnbound(t.Generic[C, P, R]):
    """Decorator to make a component support children nodes.

    This decorator is used to create a component that can accept children nodes,
    just like native htpy components.

    It lets you convert this:

    ```python
    def my_component(*, title: str, children: h.Node) -> h.Renderable:
        ...

    my_component(title="My title", children=h.div["My content"])
    ```

    To this:

    ```python
    @h.with_children
    def my_component(children: h.Node, *, title: str) -> h.Renderable:
        ...

    my_component(title="My title")[h.div["My content"]]
    ```
    """

    wrapped: Callable[t.Concatenate[C | None, P], R]

    def __init__(self, func: Callable[t.Concatenate[C | None, P], R]) -> None:
        # This instance is created at import time when decorating the component.
        # It means that this object is global, and shared between all renderings
        # of the same component.
        self.wrapped = func
        functools.update_wrapper(self, func)

    def __repr__(self) -> str:
        return f"with_children({self.wrapped.__name__}, <unbound>)"

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> _WithChildrenBound[C, P, R]:
        # This is the first call to the component, where we get the
        # component's args and kwargs:
        #
        #     my_component(title="My title")
        #
        # It is important that we return a new instance bound to the args
        # and kwargs instead of mutating, so that state doesn't leak between
        # multiple renderings of the same component.
        #
        return _WithChildrenBound(self.wrapped, args, kwargs)

    def __getitem__(self, children: C | None) -> R:
        # This is the unbound component being used with children:
        #
        #     my_component["My content"]
        #
        return self.wrapped(children)  # type: ignore[call-arg]

    def __str__(self) -> markupsafe.Markup:
        # This is the unbound component being rendered to a string:
        #
        #     str(my_component)
        #
        return markupsafe.Markup(self.wrapped(None))  # type: ignore[call-arg]

    __html__ = __str__

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)

    def iter_chunks(
        self,
        context: Mapping[htpy.Context[t.Any], t.Any] | None = None,
    ) -> Iterator[str]:
        return self.wrapped(None).iter_chunks(context)  # type: ignore[call-arg]


class _WithChildrenBound(t.Generic[C, P, R]):
    _func: Callable[t.Concatenate[C | None, P], R]
    _args: tuple[t.Any, ...]
    _kwargs: Mapping[str, t.Any]

    def __init__(
        self,
        func: Callable[t.Concatenate[C | None, P], R],
        args: tuple[t.Any, ...],
        kwargs: Mapping[str, t.Any],
    ) -> None:
        # This is called at runtime when the component is being passed args and
        # kwargs. This instance is only used for the current rendering of the
        # component.
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def __repr__(self) -> str:
        return f"with_children({self._func.__name__}, {self._args}, {self._kwargs})"

    def __getitem__(self, children: C | None) -> R:
        # This is a bound component being used with children:
        #
        #     my_component(title="My title")["My content"]
        #
        return self._func(children, *self._args, **self._kwargs)

    def __str__(self) -> markupsafe.Markup:
        # This is a bound component being rendered to a string:
        #
        #     str(my_component(title="My title"))
        #
        return markupsafe.Markup(self._func(None, *self._args, **self._kwargs))

    __html__ = __str__

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)

    def iter_chunks(
        self,
        context: Mapping[htpy.Context[t.Any], t.Any] | None = None,
    ) -> Iterator[str]:
        return self._func(None, *self._args, **self._kwargs).iter_chunks(context)


with_children = _WithChildrenUnbound
