__version__ = "0.0.1"

import types
from itertools import chain

from .attrs import BOOL_VALUE, fixup_attribute_name, generate_attrs
from .safestring import mark_safe, to_html  # noqa: F401


def as_iter(x):
    if isinstance(x, Element):
        yield from x
    else:
        yield to_html(x)


def make_list(x):
    if isinstance(x, list | types.GeneratorType):
        return x

    return [x]


class Element:
    def __init__(self, name, is_void_element=False, attrs=None, children=None):
        self.name = name
        self.is_void_element = is_void_element
        self.attrs = attrs or {}
        self.children = children or []

    def __str__(self):
        return "".join(str(x) for x in self)

    def __call__(self, *args, **kwargs):
        children_lists = [
            make_list(child) for child in args if not isinstance(child, dict)
        ]
        attrs = {
            **self.attrs,
            **{fixup_attribute_name(k): v for k, v in kwargs.items()},
        }
        for args_attrs in args:
            if isinstance(args_attrs, dict):
                attrs.update(
                    {fixup_attribute_name(k): v for k, v in args_attrs.items()}
                )

        return self._evolve(attrs, list(chain.from_iterable(children_lists))
        )

    def _evolve(self, attrs, children):
        return self.__class__(
            name=self.name,
            is_void_element=self.is_void_element,
            attrs=attrs,
            children=children,
        )

    def __iter__(self):
        attrs = " ".join(
            (f'{to_html(k)}="{v}"') if v is not BOOL_VALUE else k
            for k, v in generate_attrs(self.attrs)
        )

        yield f'<{self.name}{" " + attrs if attrs else ""}>'

        if not self.is_void_element:
            for child in self.children:
                yield from as_iter(child)

            yield f"</{self.name}>"


class ElementWithDoctype(Element):
    def __init__(self, *args, doctype, **kwargs):
        super().__init__(*args, **kwargs)
        self.doctype = doctype

    def _evolve(self, attrs, children):
       return self.__class__(
            name=self.name,
            is_void_element=self.is_void_element,
            doctype=self.doctype,
            attrs=attrs,
            children=children,
        )

    def __iter__(self):
        yield self.doctype
        yield from super().__iter__()


html = ElementWithDoctype("html", doctype='<!doctype html>')
area = Element("are", is_void_element=True)
base = Element("base", is_void_element=True)
br = Element("br", is_void_element=True)
col = Element("col", is_void_element=True)
embed = Element("embed", is_void_element=True)
hr = Element("hr", is_void_element=True)
img = Element("img", is_void_element=True)
input = Element("input", is_void_element=True)
link = Element("link", is_void_element=True)
meta = Element("meta", is_void_element=True)
param = Element("param", is_void_element=True)
source = Element("source", is_void_element=True)
track = Element("track", is_void_element=True)
wbr = Element("wbr", is_void_element=True)


def __getattr__(name):
    return Element(name)
