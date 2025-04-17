from __future__ import annotations

import functools
import keyword
import typing as t
from collections.abc import Callable, Iterable

from htpy._attributes import (
    _attrs_string,  # pyright: ignore[reportPrivateUsage]
    _id_class_names_from_css_str,  # pyright: ignore[reportPrivateUsage]
)
from htpy._contexts import ContextConsumer, ContextProvider
from htpy._fragments import Fragment
from htpy._rendering import (
    _chunks_as_markup,  # pyright: ignore[reportPrivateUsage]
    _iter_chunks_node,  # pyright: ignore[reportPrivateUsage]
)
from htpy._types import (
    _HasHtml,  # pyright: ignore[reportPrivateUsage]
    _KnownInvalidChildren,  # pyright: ignore[reportPrivateUsage]
)

try:
    from warnings import deprecated  # type: ignore[attr-defined,unused-ignore]
except ImportError:
    from typing_extensions import deprecated

if t.TYPE_CHECKING:
    from collections.abc import Iterator, Mapping
    from types import UnionType

    import markupsafe

    from htpy._contexts import Context
    from htpy._types import Attribute, Node


BaseElementSelf = t.TypeVar("BaseElementSelf", bound="BaseElement")
ElementSelf = t.TypeVar("ElementSelf", bound="Element")


class BaseElement:
    __slots__ = ("_name", "_attrs", "_children")

    def __init__(self, name: str, attrs_str: str = "", children: Node = None) -> None:
        self._name = name
        self._attrs = attrs_str
        self._children = children

    def __str__(self) -> markupsafe.Markup:
        return _chunks_as_markup(self)

    __html__ = __str__

    @t.overload
    def __call__(
        self: BaseElementSelf, id_class: str, attrs: Mapping[str, Attribute], **kwargs: Attribute
    ) -> BaseElementSelf: ...
    @t.overload
    def __call__(
        self: BaseElementSelf, id_class: str = "", **kwargs: Attribute
    ) -> BaseElementSelf: ...
    @t.overload
    def __call__(
        self: BaseElementSelf, attrs: Mapping[str, Attribute], **kwargs: Attribute
    ) -> BaseElementSelf: ...
    @t.overload
    def __call__(self: BaseElementSelf, **kwargs: Attribute) -> BaseElementSelf: ...
    def __call__(self: BaseElementSelf, *args: t.Any, **kwargs: t.Any) -> BaseElementSelf:
        id_class = ""
        attrs: Mapping[str, Attribute] = {}

        if len(args) == 1:
            if isinstance(args[0], str):
                # element(".foo")
                id_class = args[0]
                attrs = {}
            else:
                # element({"foo": "bar"})
                id_class = ""
                attrs = args[0]
        elif len(args) == 2:
            # element(".foo", {"bar": "baz"})
            id_class, attrs = args

        return self.__class__(
            self._name,
            _attrs_string(
                {
                    **(_id_class_names_from_css_str(id_class) if id_class else {}),
                    **attrs,
                    **{_python_to_html_name(k): v for k, v in kwargs.items()},
                }
            ),
            self._children,
        )

    @deprecated(  # type: ignore[misc,unused-ignore]
        "iterating over an element is deprecated and will be removed in a future release. "
        "Please use the element.iter_chunks() method instead."
    )  # pyright: ignore [reportUntypedFunctionDecorator]
    def __iter__(self) -> Iterator[str]:
        return self.iter_chunks()

    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        yield f"<{self._name}{self._attrs}>"
        yield from _iter_chunks_node(self._children, context)
        yield f"</{self._name}>"

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)

    # Avoid having Django "call" a htpy element that is injected into a
    # template. Setting do_not_call_in_templates will prevent Django from doing
    # an extra call:
    # https://docs.djangoproject.com/en/5.0/ref/templates/api/#variables-and-lookups
    do_not_call_in_templates = True


def _validate_children(children: t.Any) -> None:
    # Non-lazy iterables:
    # list and tuple are iterables and part of _KnownValidChildren. Since we
    # know they can be consumed multiple times, we validate them recursively now
    # rather than at render time to provide better error messages.
    if isinstance(children, list | tuple):
        for child in children:  # pyright: ignore[reportUnknownVariableType]
            _validate_children(child)
        return

    # bytes, bytearray etc:
    # These are Iterable (part of _KnownValidChildren) but still not
    # useful as a child node.
    if isinstance(children, _KnownInvalidChildren):
        raise TypeError(f"{children!r} is not a valid child element")

    # Element, str, int and all other regular/valid types.
    if isinstance(children, _KnownValidChildren):
        return

    # Arbitrary objects that are not valid children.
    raise TypeError(f"{children!r} is not a valid child element")


class Element(BaseElement):
    def __getitem__(self: ElementSelf, children: Node) -> ElementSelf:
        _validate_children(children)
        return self.__class__(self._name, self._attrs, children)  # pyright: ignore [reportUnknownArgumentType]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '<{self._name}{self._attrs}>...</{self._name}>'>"


class HTMLElement(Element):
    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        yield "<!doctype html>"
        yield from super().iter_chunks(context)


class VoidElement(BaseElement):
    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        yield f"<{self._name}{self._attrs}>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '<{self._name}{self._attrs}>'>"


def _python_to_html_name(name: str) -> str:
    # Make _hyperscript (https://hyperscript.org/) work smoothly
    if name == "_":
        return "_"

    html_name = name
    name_without_underscore_suffix = name.removesuffix("_")
    if keyword.iskeyword(name_without_underscore_suffix):
        html_name = name_without_underscore_suffix
    html_name = html_name.replace("_", "-")

    return html_name


@functools.lru_cache(maxsize=300)
def _get_element(name: str) -> Element:  # pyright: ignore[reportUnusedFunction]
    if not name.islower():
        raise AttributeError(
            f"{name} is not a valid element name. html elements must have all lowercase names"
        )
    return Element(_python_to_html_name(name))


_KnownValidChildren: UnionType = (
    None
    | BaseElement
    | ContextProvider  # pyright: ignore[reportMissingTypeArgument]
    | ContextConsumer  # pyright: ignore[reportMissingTypeArgument]
    | str
    | int
    | Fragment
    | _HasHtml
    | Callable
    | Iterable
)
