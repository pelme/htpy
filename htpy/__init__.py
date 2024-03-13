__version__ = "24.3.13"
__all__ = []

import functools
import types

from markupsafe import Markup as _Markup
from markupsafe import escape as _escape


def _force_escape(value):
    return _escape(str(value))


# Inspired by https://www.npmjs.com/package/classnames
def _class_names(value):
    if isinstance(value, list | tuple | set):
        return _Markup(" ").join(
            result for x in value if (result := _dict_class_names(x) if isinstance(x, dict) else x)
        )

    if isinstance(value, dict):
        return _dict_class_names(value)

    return _force_escape(value)


def _dict_class_names(value):
    return _Markup(" ").join(k for k, v in value.items() if v)


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
        if key == "class":
            yield ("class", _class_names(value))

        elif value in (False, None):
            continue

        elif value is True:
            yield _force_escape(key), True

        else:
            yield _force_escape(key), _force_escape(value)


def _iter_children(x):
    while not isinstance(x, BaseElement) and callable(x):
        x = x()

    if isinstance(x, BaseElement):
        yield from x
    elif hasattr(x, "__html__"):
        yield x.__html__()
    elif isinstance(x, tuple | list | types.GeneratorType):
        for child in x:
            yield from _iter_children(child)
    elif x is not None:
        yield _escape(x)


class BaseElement:
    def __init__(self, name, attrs, children):
        self._name = name
        self._attrs = attrs
        self._children = children

    def __str__(self):
        return _Markup("".join(str(x) for x in self))

    def __call__(self, *args, **kwargs):
        if len(args) == 0:
            id_class = ""
            attrs = {}
        elif len(args) == 1:
            if isinstance(args[0], str):
                # element(".foo")
                id_class = args[0]
                attrs = {}
            else:
                # element({"foo": "bar"})
                id_class = ""
                attrs = args[0]
        if len(args) == 2:
            # element(".foo", {"bar": "baz"})
            id_class, attrs = args

        return self._evolve(
            attrs={
                **(_id_class_names_from_css_str(id_class) if id_class else {}),
                **attrs,
                **{_kwarg_attribute_name(k): v for k, v in kwargs.items()},
            },
        )

    def _evolve(self, attrs=None, children=None, **kwargs):
        return self.__class__(
            name=self._name,
            attrs=attrs or self._attrs,
            children=children or self._children,
            **kwargs,
        )

    def _attrs_string(self):
        result = " ".join(k if v is True else f'{k}="{v}"' for k, v in _generate_attrs(self._attrs))

        if not result:
            return ""

        return " " + result

    def __iter__(self):
        yield f"<{self._name}{self._attrs_string()}>"
        yield from _iter_children(self._children)
        yield f"</{self._name}>"

    def __repr__(self):
        return f"<{self.__class__.__name__} '{self}'>"


class Element(BaseElement):
    def __getitem__(self, children):
        return self._evolve(children=children)


class HTMLElement(Element):
    def __iter__(self):
        yield "<!doctype html>"
        yield from super().__iter__()


class VoidElement(BaseElement):
    def __iter__(self):
        yield f"<{self._name}{self._attrs_string()}>"


# https://developer.mozilla.org/en-US/docs/Glossary/Doctype
html = HTMLElement("html", {}, [])

# https://developer.mozilla.org/en-US/docs/Glossary/Void_element
area = VoidElement("area", {}, [])
base = VoidElement("base", {}, [])
br = VoidElement("br", {}, [])
col = VoidElement("col", {}, [])
embed = VoidElement("embed", {}, [])
hr = VoidElement("hr", {}, [])
img = VoidElement("img", {}, [])
input = VoidElement("input", {}, [])
link = VoidElement("link", {}, [])
meta = VoidElement("meta", {}, [])
param = VoidElement("param", {}, [])
source = VoidElement("source", {}, [])
track = VoidElement("track", {}, [])
wbr = VoidElement("wbr", {}, [])


@functools.lru_cache(maxsize=300)
def __getattr__(name):
    if not name.islower():
        raise AttributeError(
            f"{name} is not a valid element name. html elements must have all lowercase names"
        )
    return Element(name.replace("_", "-"), {}, [])
