__version__ = "24.3.14"
__all__ = []

import functools
from collections.abc import Iterable

from markupsafe import Markup as _Markup
from markupsafe import escape as _escape


def _force_escape(value):
    return _escape(str(value))


# Inspired by https://www.npmjs.com/package/classnames
def _class_names(items):
    if isinstance(items, str):
        return _force_escape(items)

    if isinstance(items, dict) or not isinstance(items, Iterable):
        items = [items]

    return " ".join(_force_escape(class_name) for class_name in _class_names_for_items(items))


def _class_names_for_items(items):
    for item in items:
        if isinstance(item, dict):
            for k, v in item.items():
                if v:
                    yield k
        else:
            if item:
                yield item


def _id_class_names_from_css_str(x):
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

    result = {}
    if ids:
        result["id"] = ids[0]

    if classes:
        result["class"] = " ".join(classes)

    return result


def _kwarg_attribute_name(name):
    # Make _hyperscript (https://hyperscript.org/) work smoothly
    if name == "_":
        return "_"

    return name.removesuffix("_").replace("_", "-")


def _generate_attrs(raw_attrs):
    for key, value in raw_attrs.items():
        if value in (False, None):
            continue

        if key == "class":
            yield ("class", _class_names(value))

        elif value is True:
            yield _force_escape(key), True

        else:
            yield _force_escape(key), _force_escape(value)


def _attrs_string(attrs):
    result = " ".join(k if v is True else f'{k}="{v}"' for k, v in _generate_attrs(attrs))

    if not result:
        return ""

    return " " + result


def _iter_children(x):
    while not isinstance(x, BaseElement) and callable(x):
        x = x()

    if x is None:
        return

    if isinstance(x, BaseElement):
        yield from x
    elif isinstance(x, str) or hasattr(x, "__html__"):
        yield _escape(x)
    elif isinstance(x, Iterable):
        for child in x:
            yield from _iter_children(child)
    else:
        raise ValueError(f"{x!r} is not a valid child element")


class BaseElement:
    __slots__ = ("_name", "_attrs", "_children")

    def __init__(self, name, attrs, children):
        self._name = name
        self._attrs = attrs
        self._children = children

    def __str__(self):
        return _Markup("".join(str(x) for x in self))

    def __call__(self, *args, **kwargs):
        id_class = ""
        attrs = {}

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

    def __iter__(self):
        yield f"<{self._name}{_attrs_string(self._attrs)}>"
        yield from _iter_children(self._children)
        yield f"</{self._name}>"

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self}'>"


class Element(BaseElement):
    def __getitem__(self, children):
        return self.__class__(self._name, self._attrs, children)


class HTMLElement(Element):
    def __iter__(self):
        yield "<!doctype html>"
        yield from super().__iter__()


class VoidElement(BaseElement):
    def __iter__(self):
        yield f"<{self._name}{_attrs_string(self._attrs)}>"


# https://developer.mozilla.org/en-US/docs/Glossary/Doctype
html = HTMLElement("html", {}, None)

# https://developer.mozilla.org/en-US/docs/Glossary/Void_element
area = VoidElement("area", {}, None)
base = VoidElement("base", {}, None)
br = VoidElement("br", {}, None)
col = VoidElement("col", {}, None)
embed = VoidElement("embed", {}, None)
hr = VoidElement("hr", {}, None)
img = VoidElement("img", {}, None)
input = VoidElement("input", {}, None)
link = VoidElement("link", {}, None)
meta = VoidElement("meta", {}, None)
param = VoidElement("param", {}, None)
source = VoidElement("source", {}, None)
track = VoidElement("track", {}, None)
wbr = VoidElement("wbr", {}, None)


@functools.lru_cache(maxsize=300)
def __getattr__(name):
    if not name.islower():
        raise AttributeError(
            f"{name} is not a valid element name. html elements must have all lowercase names"
        )
    return Element(name.replace("_", "-"), {}, None)
