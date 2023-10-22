__version__ = "0.0.1"


from .attrs import fixup_attribute_name, generate_attrs, BOOL_VALUE
from .safestring import  to_html, mark_safe



def as_iter(x):
    if isinstance(x, Element):
        yield from x
    else:
        yield to_html(x)


class Element:
    def __init__(self, name, is_void_element=False, attributes=None, children=None):
        self.name = name
        self.is_void_element = is_void_element
        self.attributes = attributes or {}
        self.children = children or []

    def __str__(self):
        return "".join(str(x) for x in self)

    def __call__(self, *args, **kwargs):
        children = [child for child in args if not isinstance(child, dict)]
        attrs = {
            **self.attributes,
            **{fixup_attribute_name(k): v for k, v in kwargs.items()},
        }
        for args_attrs in args:
            if isinstance(args_attrs, dict):
                attrs.update(
                    {fixup_attribute_name(k): v for k, v in args_attrs.items()}
                )

        return Element(
            name=self.name,
            is_void_element=self.is_void_element,
            attributes=attrs,
            children=children,
        )

    def __iter__(self):
        attrs = " ".join(
            (f'{to_html(k)}="{v}"') if v is not BOOL_VALUE else k
            for k, v in generate_attrs(self.attributes)
        )

        yield f'<{self.name}{" " + attrs if attrs else ""}>'

        if not self.is_void_element:
            for child in self.children:
                yield from as_iter(child)

            yield f"</{self.name}>"


div = Element("div")
p = Element("p")
ul = Element("ul")
li = Element("li")
html = Element("html")
head = Element("head")
body = Element("body")
button = Element("button")
script = Element("script")
link = Element("link", is_void_element=True)
input = Element("input", is_void_element=True)
