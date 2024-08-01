from __future__ import annotations

__version__ = "24.7.2"
__all__: list[str] = []

import functools
from collections.abc import Callable, Iterable, Iterator
from typing import Any, Protocol, TypeAlias, TypeVar, overload

from markupsafe import Markup as _Markup
from markupsafe import escape as _escape

from . import elements

BaseElementSelf = TypeVar("BaseElementSelf", bound="BaseElement")
ElementSelf = TypeVar("ElementSelf", bound="Element")


def _force_escape(value: Any) -> str:
    return _escape(str(value))


# Inspired by https://www.npmjs.com/package/classnames
def _class_names(items: Any) -> Any:
    if isinstance(items, str):
        return _force_escape(items)

    if isinstance(items, dict) or not isinstance(items, Iterable):
        items = [items]

    result = list(_class_names_for_items(items))
    if not result:
        return False

    return " ".join(_force_escape(class_name) for class_name in result)


def _class_names_for_items(items: Any) -> Any:
    for item in items:
        if isinstance(item, dict):
            for k, v in item.items():  # pyright: ignore [reportUnknownVariableType]
                if v:
                    yield k
        else:
            if item:
                yield item


def _id_class_names_from_css_str(x: Any) -> dict[str, Attribute]:
    if not isinstance(x, str):
        raise ValueError(f"id/class strings must be str. got {x}")

    if "#" in x and "." in x and x.find("#") > x.find("."):
        raise ValueError("id (#) must be specified before classes (.)")

    if x[0] not in ".#":
        raise ValueError("id/class strings must start with # or .")

    parts = x.split(".")
    ids = [part.removeprefix("#") for part in parts if part.startswith("#")]
    classes = [part for part in parts if not part.startswith("#") if part]

    assert len(ids) in (0, 1)

    result: dict[str, Attribute] = {}
    if ids:
        result["id"] = ids[0]

    if classes:
        result["class"] = " ".join(classes)

    return result


def _kwarg_attribute_name(name: str) -> str:
    # Make _hyperscript (https://hyperscript.org/) work smoothly
    if name == "_":
        return "_"

    return name.removesuffix("_").replace("_", "-")


def _generate_attrs(raw_attrs: dict[str, Attribute]) -> Iterable[tuple[str, Attribute]]:
    for key, value in raw_attrs.items():
        if value in (False, None):
            continue

        if key == "class":
            if result := _class_names(value):
                yield ("class", result)

        elif value is True:
            yield _force_escape(key), True

        else:
            yield _force_escape(key), _force_escape(value)


def _attrs_string(attrs: dict[str, Attribute]) -> str:
    result = " ".join(k if v is True else f'{k}="{v}"' for k, v in _generate_attrs(attrs))

    if not result:
        return ""

    return " " + result


def iter_node(x: Node) -> Iterator[str]:
    while not isinstance(x, BaseElement) and callable(x):
        x = x()

    if x is None:
        return

    if isinstance(x, BaseElement):
        yield from x
    elif isinstance(x, str) or hasattr(x, "__html__"):
        yield str(_escape(x))
    elif isinstance(x, Iterable):
        for child in x:
            yield from iter_node(child)
    else:
        raise ValueError(f"{x!r} is not a valid child element")


@functools.lru_cache(maxsize=300)
def _get_element(name: str) -> Element:
    if not name.islower():
        raise AttributeError(
            f"{name} is not a valid element name. html elements must have all lowercase names"
        )
    return Element(name.replace("_", "-"), {}, None)


def __getattr__(name: str) -> Element:
    return _get_element(name)


class BaseElement:
    __slots__ = ("_name", "_attrs", "_children")

    def __init__(self, name: str, attrs: dict[str, Attribute], children: Node) -> None:
        self._name = name
        self._attrs = attrs
        self._children = children

    def __str__(self) -> _Markup:
        return _Markup("".join(str(x) for x in self))

    @overload
    def __call__(
        self: BaseElementSelf, id_class: str, attrs: dict[str, Attribute], **kwargs: Attribute
    ) -> BaseElementSelf: ...
    @overload
    def __call__(
        self: BaseElementSelf, id_class: str = "", **kwargs: Attribute
    ) -> BaseElementSelf: ...
    @overload
    def __call__(
        self: BaseElementSelf, attrs: dict[str, Attribute], **kwargs: Attribute
    ) -> BaseElementSelf: ...
    @overload
    def __call__(self: BaseElementSelf, **kwargs: Attribute) -> BaseElementSelf: ...
    def __call__(self: BaseElementSelf, *args: Any, **kwargs: Any) -> BaseElementSelf:
        id_class = ""
        attrs: dict[str, Attribute] = {}

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
            {
                **(_id_class_names_from_css_str(id_class) if id_class else {}),
                **attrs,
                **{_kwarg_attribute_name(k): v for k, v in kwargs.items()},
            },
            self._children,
        )

    def __iter__(self) -> Iterator[str]:
        yield f"<{self._name}{_attrs_string(self._attrs)}>"
        yield from iter_node(self._children)
        yield f"</{self._name}>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self}'>"

    # Avoid having Django "call" a htpy element that is injected into a
    # template. Setting do_not_call_in_templates will prevent Django from doing
    # an extra call:
    # https://docs.djangoproject.com/en/5.0/ref/templates/api/#variables-and-lookups
    do_not_call_in_templates = True


class Element(BaseElement):
    def __getitem__(self: ElementSelf, children: Node) -> ElementSelf:
        return self.__class__(self._name, self._attrs, children)


class HTMLElement(Element):
    def __iter__(self) -> Iterator[str]:
        yield "<!doctype html>"
        yield from super().__iter__()


class VoidElement(BaseElement):
    def __iter__(self) -> Iterator[str]:
        yield f"<{self._name}{_attrs_string(self._attrs)}>"


def render_node(node: Node) -> _Markup:
    return _Markup("".join(iter_node(node)))


class _HasHtml(Protocol):
    def __html__(self) -> str: ...


_ClassNamesDict: TypeAlias = dict[str, bool]
_ClassNames: TypeAlias = Iterable[str | None | bool | _ClassNamesDict] | _ClassNamesDict
Node: TypeAlias = None | str | BaseElement | _HasHtml | Iterable["Node"] | Callable[[], "Node"]

Attribute: TypeAlias = None | bool | str | _HasHtml | _ClassNames

# https://developer.mozilla.org/en-US/docs/Glossary/Doctype
html = HTMLElement("html", {}, None)

for name in elements.void_elements:
    globals()[name] = VoidElement(name, {}, None)

for name in elements.elements:
    globals()[name] = Element(name, {}, None)
