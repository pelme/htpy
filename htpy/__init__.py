from __future__ import annotations

__version__ = "24.6.1"
__all__: list[str] = []

import functools
from collections.abc import Callable, Iterable, Iterator
from typing import Any, Protocol, TypeAlias, TypeVar, overload

from markupsafe import Markup as _Markup
from markupsafe import escape as _escape

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


def _iter_children(x: Node) -> Iterator[str]:
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
            yield from _iter_children(child)
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
        yield from _iter_children(self._children)
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


class _HasHtml(Protocol):
    def __html__(self) -> str: ...


_ClassNamesDict: TypeAlias = dict[str, bool]
_ClassNames: TypeAlias = Iterable[str | None | bool | _ClassNamesDict] | _ClassNamesDict
Node: TypeAlias = None | str | BaseElement | _HasHtml | Iterable["Node"] | Callable[[], "Node"]

Attribute: TypeAlias = None | bool | str | _HasHtml | _ClassNames

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

# Non-deprecated HTML elements, extracted from
# https://developer.mozilla.org/en-US/docs/Web/HTML/Element
# Located via the inspector with:
# Array.from($0.querySelectorAll('li')).filter(x=>!x.querySelector('.icon-deprecated')).map(x => x.querySelector('code').textContent) # noqa: E501
a = Element("a", {}, None)
abbr = Element("abbr", {}, None)
abc = Element("abc", {}, None)
address = Element("address", {}, None)
article = Element("article", {}, None)
aside = Element("aside", {}, None)
audio = Element("audio", {}, None)
b = Element("b", {}, None)
bdi = Element("bdi", {}, None)
bdo = Element("bdo", {}, None)
blockquote = Element("blockquote", {}, None)
body = Element("body", {}, None)
button = Element("button", {}, None)
canvas = Element("canvas", {}, None)
caption = Element("caption", {}, None)
cite = Element("cite", {}, None)
code = Element("code", {}, None)
colgroup = Element("colgroup", {}, None)
data = Element("data", {}, None)
datalist = Element("datalist", {}, None)
dd = Element("dd", {}, None)
del_ = Element("del_", {}, None)
details = Element("details", {}, None)
dfn = Element("dfn", {}, None)
dialog = Element("dialog", {}, None)
div = Element("div", {}, None)
dl = Element("dl", {}, None)
dt = Element("dt", {}, None)
em = Element("em", {}, None)
fieldset = Element("fieldset", {}, None)
figcaption = Element("figcaption", {}, None)
figure = Element("figure", {}, None)
footer = Element("footer", {}, None)
form = Element("form", {}, None)
h1 = Element("h1", {}, None)
h2 = Element("h2", {}, None)
h3 = Element("h3", {}, None)
h4 = Element("h4", {}, None)
h5 = Element("h5", {}, None)
h6 = Element("h6", {}, None)
head = Element("head", {}, None)
header = Element("header", {}, None)
hgroup = Element("hgroup", {}, None)
i = Element("i", {}, None)
iframe = Element("iframe", {}, None)
ins = Element("ins", {}, None)
kbd = Element("kbd", {}, None)
label = Element("label", {}, None)
legend = Element("legend", {}, None)
li = Element("li", {}, None)
main = Element("main", {}, None)
map = Element("map", {}, None)
mark = Element("mark", {}, None)
menu = Element("menu", {}, None)
meter = Element("meter", {}, None)
nav = Element("nav", {}, None)
noscript = Element("noscript", {}, None)
object = Element("object", {}, None)
ol = Element("ol", {}, None)
optgroup = Element("optgroup", {}, None)
option = Element("option", {}, None)
output = Element("output", {}, None)
p = Element("p", {}, None)
picture = Element("picture", {}, None)
portal = Element("portal", {}, None)
pre = Element("pre", {}, None)
progress = Element("progress", {}, None)
q = Element("q", {}, None)
rp = Element("rp", {}, None)
rt = Element("rt", {}, None)
ruby = Element("ruby", {}, None)
s = Element("s", {}, None)
samp = Element("samp", {}, None)
script = Element("script", {}, None)
search = Element("search", {}, None)
section = Element("section", {}, None)
select = Element("select", {}, None)
slot = Element("slot", {}, None)
small = Element("small", {}, None)
span = Element("span", {}, None)
strong = Element("strong", {}, None)
style = Element("style", {}, None)
sub = Element("sub", {}, None)
summary = Element("summary", {}, None)
sup = Element("sup", {}, None)
table = Element("table", {}, None)
tbody = Element("tbody", {}, None)
td = Element("td", {}, None)
template = Element("template", {}, None)
textarea = Element("textarea", {}, None)
tfoot = Element("tfoot", {}, None)
th = Element("th", {}, None)
thead = Element("thead", {}, None)
time = Element("time", {}, None)
title = Element("title", {}, None)
tr = Element("tr", {}, None)
u = Element("u", {}, None)
ul = Element("ul", {}, None)
var = Element("var", {}, None)
