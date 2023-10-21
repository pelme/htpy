__version__ = "0.0.1"


from .attrs import generate_attrs
from .safestring import _SafeString, to_html


def mark_safe(value):
    return _SafeString(value)


def as_iter(x):
    if isinstance(x, Element):
        yield from x
    else:
        yield to_html(x)


class Element:
    def __init__(self, name, attributes, children):
        self.name = name
        self.attributes = attributes
        self.children = children

    def __str__(self):
        return "".join(str(x) for x in self)

    def __call__(self, *children):
        assert not self.children
        return Element(self.name, self.attributes, children)

    def __iter__(self):
        attrs = " ".join(f'{k}="{v}"' for k, v in generate_attrs(self.attributes))

        yield f'<{self.name}{" " + attrs if attrs else ""}>'

        for child in self.children:
            yield from as_iter(child)

        yield f"</{self.name}>"


class ElementType:
    def __init__(self, name: str) -> None:
        self.name = name

    def __call__(self, *children, **attrs):
        return Element(self.name, attrs, children)


div = ElementType("div")
p = ElementType("p")
ul = ElementType("ul")
li = ElementType("li")
html = ElementType("html")
head = ElementType("head")
body = ElementType("body")
script = ElementType("script")
