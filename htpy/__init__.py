__version__ = "24.3"
import functools
import types

from ._attrs import generate_attrs, id_classnames_from_css_str, kwarg_attribute_name
from ._markup import Markup, to_html


def _iter_children(x):
    if isinstance(x, Element):
        yield from x
    else:
        if x is not False and x is not None:
            yield to_html(x, quote=False)


def _flatten_children(children):
    for x in children:
        if isinstance(x, tuple | list | types.GeneratorType):
            yield from _flatten_children(x)
        else:
            yield x


class BaseElement:
    def __init__(self, name, attrs, children):
        self._name = name
        self._attrs = attrs
        self._children = children

    def __str__(self):
        return Markup("".join(str(x) for x in self))

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
                **(id_classnames_from_css_str(id_class) if id_class else {}),
                **attrs,
                **{kwarg_attribute_name(k): v for k, v in kwargs.items()},
            },
        )

    def _evolve(self, attrs=None, children=None, **kwargs):
        return self.__class__(
            name=self._name,
            attrs=attrs or dict(self._attrs),
            children=children or list(self._children),
            **kwargs,
        )

    def _attrs_string(self):
        result = " ".join(k if v is True else f'{k}="{v}"' for k, v in generate_attrs(self._attrs))

        if not result:
            return ""

        return " " + result

    def __iter__(self):
        yield f"<{self._name}{self._attrs_string()}>"

        for child in self._children:
            yield from _iter_children(child)

        yield f"</{self._name}>"

    def __repr__(self):
        return f"<htpy element '{self}'>"


class Element(BaseElement):
    def __getitem__(self, children):
        if not isinstance(children, tuple):
            children = (children,)

        return self._evolve(
            children=list(_flatten_children(children)),
        )


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


@functools.lru_cache(maxsize=300)
def __getattr__(name):
    return Element(name.replace("_", "-"), {}, [])


__all__ = []
