__version__ = "23.0"

import types
from itertools import chain

from .attrs import generate_attrs, kwarg_attribute_name
from .safestring import SafeString, mark_safe, to_html  # noqa: F401


def _iter_children(x):
    if isinstance(x, Element):
        yield from x
    else:
        yield to_html(x, quote=False)


def _make_list(x):
    if isinstance(x, list | types.GeneratorType):
        return x

    return [x]


class Element:
    def __init__(self, name, attrs, children):
        self._name = name
        self._attrs = attrs
        self._children = children

    def __str__(self):
        return "".join(str(x) for x in self)

    def __call__(self, *args, **kwargs):
        # element({"foo": "bar"}) -- dict attributes
        if len(args) == 1 and isinstance(args[0], dict):
            if kwargs:
                raise TypeError(
                    "Pass attributes either by a single dictionary or key word arguments - not both."
                )
            return self._evolve(attrs={**self._attrs, **args[0]})

        # element("foo", "bar") -- children
        elif args:
            if kwargs:
                raise TypeError(
                    "Pass attributes or children, not both. "
                    "Hint: Add a new set of parenthesis to pass both attributes and children: "
                    f'{self._name}(attr="value")("children")'
                )
            return self._evolve(
                children=list(chain.from_iterable(_make_list(child) for child in args)),
            )
        # element(foo="bar") -- kwargs attributes
        elif kwargs:
            return self._evolve(
                attrs={
                    **self._attrs,
                    **{kwarg_attribute_name(k): v for k, v in kwargs.items()},
                },
            )

        # element()
        return self

    def _evolve(self, attrs=None, children=None, **kwargs):
        return self.__class__(
            name=self._name,
            attrs=attrs or dict(self._attrs),
            children=children or list(self._children),
            **kwargs,
        )

    def _attrs_string(self):
        result = " ".join(
            k if v is True else f'{k}="{v}"' for k, v in generate_attrs(self._attrs)
        )

        if not result:
            return ""

        return " " + result

    def __iter__(self):
        yield f"<{self._name}{self._attrs_string()}>"

        for child in self._children:
            yield from _iter_children(child)

        yield f"</{self._name}>"


class ElementWithDoctype(Element):
    def __init__(self, *args, doctype, **kwargs):
        super().__init__(*args, **kwargs)
        self._doctype = doctype

    def _evolve(self, **kwargs):
        return super()._evolve(doctype=self._doctype, **kwargs)

    def __iter__(self):
        yield self._doctype
        yield from super().__iter__()


class VoidElement(Element):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self._children:
            raise ValueError(f"{self._name} elements cannot have children")

    def __iter__(self):
        yield f"<{self._name}{self._attrs_string()}>"


# https://developer.mozilla.org/en-US/docs/Glossary/Doctype
html = ElementWithDoctype("html", {}, [], doctype="<!doctype html>")

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


def __getattr__(name):
    return Element(name.replace("_", "-"), {}, [])


__all__ = []
