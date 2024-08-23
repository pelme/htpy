from __future__ import annotations

__version__ = "24.8.2"
__all__: list[str] = []

import dataclasses
import functools
import typing as t
from collections.abc import Callable, Iterable, Iterator

from markupsafe import Markup as _Markup
from markupsafe import escape as _escape

BaseElementSelf = t.TypeVar("BaseElementSelf", bound="BaseElement")
ElementSelf = t.TypeVar("ElementSelf", bound="Element")


def _force_escape(value: t.Any) -> str:
    return _escape(str(value))


# Inspired by https://www.npmjs.com/package/classnames
def _class_names(items: t.Any) -> t.Any:
    if isinstance(items, str):
        return _force_escape(items)

    if isinstance(items, dict) or not isinstance(items, Iterable):
        items = [items]

    result = list(_class_names_for_items(items))
    if not result:
        return False

    return " ".join(_force_escape(class_name) for class_name in result)


def _class_names_for_items(items: t.Any) -> t.Any:
    for item in items:
        if isinstance(item, dict):
            for k, v in item.items():  # pyright: ignore [reportUnknownVariableType]
                if v:
                    yield k
        else:
            if item:
                yield item


def _id_class_names_from_css_str(x: t.Any) -> dict[str, Attribute]:
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
        if not isinstance(key, str):  # pyright: ignore [reportUnnecessaryIsInstance]
            raise ValueError("Attribute key must be a string")

        if value is False or value is None:
            continue

        if key == "class":
            if result := _class_names(value):
                yield ("class", result)

        elif value is True:
            yield _force_escape(key), True

        else:
            if not isinstance(value, str | _HasHtml):
                raise ValueError(f"Attribute value must be a string , got {value!r}")

            yield _force_escape(key), _force_escape(value)


def _attrs_string(attrs: dict[str, Attribute]) -> str:
    result = " ".join(k if v is True else f'{k}="{v}"' for k, v in _generate_attrs(attrs))

    if not result:
        return ""

    return " " + result


T = t.TypeVar("T")
P = t.ParamSpec("P")


@dataclasses.dataclass(frozen=True)
class ContextProvider(t.Generic[T]):
    context: Context[T]
    value: T
    func: Callable[[], Node]

    def __iter__(self) -> Iterator[str]:
        return iter_node(self)

    def __str__(self) -> str:
        return render_node(self)


@dataclasses.dataclass(frozen=True)
class ContextConsumer(t.Generic[T]):
    context: Context[T]
    debug_name: str
    func: Callable[[T], Node]


class _NO_DEFAULT:
    pass


class Context(t.Generic[T]):
    def __init__(self, name: str, *, default: T | type[_NO_DEFAULT] = _NO_DEFAULT) -> None:
        self.name = name
        self.default = default

    def provider(self, value: T, children_func: Callable[[], Node]) -> ContextProvider[T]:
        return ContextProvider(self, value, children_func)

    def consumer(
        self,
        func: Callable[t.Concatenate[T, P], Node],
    ) -> Callable[P, ContextConsumer[T]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> ContextConsumer[T]:
            return ContextConsumer(self, func.__name__, lambda value: func(value, *args, **kwargs))

        return wrapper


def iter_node(x: Node) -> Iterator[str]:
    return _iter_node_context(x, {})


def _iter_node_context(x: Node, context_dict: dict[Context[t.Any], t.Any]) -> Iterator[str]:
    while not isinstance(x, BaseElement) and callable(x):
        x = x()

    if x is None:
        return

    if x is True:
        return

    if x is False:
        return

    if isinstance(x, BaseElement):
        yield from x._iter_context(context_dict)  # pyright: ignore [reportPrivateUsage]
    elif isinstance(x, ContextProvider):
        yield from _iter_node_context(x.func(), {**context_dict, x.context: x.value})  # pyright: ignore [reportUnknownMemberType]
    elif isinstance(x, ContextConsumer):
        context_value = context_dict.get(x.context, x.context.default)
        if context_value is _NO_DEFAULT:
            raise LookupError(
                f'Context value for "{x.context.name}" does not exist, '
                f"requested by {x.debug_name}()."
            )
        yield from _iter_node_context(x.func(context_value), context_dict)
    elif isinstance(x, str | _HasHtml):
        yield str(_escape(x))
    elif isinstance(x, Iterable):  # pyright: ignore [reportUnnecessaryIsInstance]
        for child in x:
            yield from _iter_node_context(child, context_dict)
    else:
        raise ValueError(f"{x!r} is not a valid child element")


@functools.lru_cache(maxsize=300)
def _get_element(name: str) -> Element:
    if not name.islower():
        raise AttributeError(
            f"{name} is not a valid element name. html elements must have all lowercase names"
        )
    return Element(name.replace("_", "-"))


def __getattr__(name: str) -> Element:
    return _get_element(name)


class BaseElement:
    __slots__ = ("_name", "_attrs", "_children")

    def __init__(
        self, name: str, attrs: dict[str, Attribute] | None = None, children: Node = None
    ) -> None:
        self._name = name
        self._attrs = attrs or {}
        self._children = children

    def __str__(self) -> _Markup:
        return _Markup("".join(str(x) for x in self))

    @t.overload
    def __call__(
        self: BaseElementSelf, id_class: str, attrs: dict[str, Attribute], **kwargs: Attribute
    ) -> BaseElementSelf: ...
    @t.overload
    def __call__(
        self: BaseElementSelf, id_class: str = "", **kwargs: Attribute
    ) -> BaseElementSelf: ...
    @t.overload
    def __call__(
        self: BaseElementSelf, attrs: dict[str, Attribute], **kwargs: Attribute
    ) -> BaseElementSelf: ...
    @t.overload
    def __call__(self: BaseElementSelf, **kwargs: Attribute) -> BaseElementSelf: ...
    def __call__(self: BaseElementSelf, *args: t.Any, **kwargs: t.Any) -> BaseElementSelf:
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
        return self._iter_context({})

    def _iter_context(self, ctx: dict[Context[t.Any], t.Any]) -> Iterator[str]:
        yield f"<{self._name}{_attrs_string(self._attrs)}>"
        yield from _iter_node_context(self._children, ctx)
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
    def _iter_context(self, ctx: dict[Context[t.Any], t.Any]) -> Iterator[str]:
        yield "<!doctype html>"
        yield from super()._iter_context(ctx)


class VoidElement(BaseElement):
    def _iter_context(self, ctx: dict[Context[t.Any], t.Any]) -> Iterator[str]:
        yield f"<{self._name}{_attrs_string(self._attrs)}>"


def render_node(node: Node) -> _Markup:
    return _Markup("".join(iter_node(node)))


def comment(text: str) -> _Markup:
    escaped_text = text.replace("--", "")
    return _Markup(f"<!-- {escaped_text} -->")


@t.runtime_checkable
class _HasHtml(t.Protocol):
    def __html__(self) -> str: ...


_ClassNamesDict: t.TypeAlias = dict[str, bool]
_ClassNames: t.TypeAlias = Iterable[str | None | bool | _ClassNamesDict] | _ClassNamesDict
Node: t.TypeAlias = (
    None
    | bool
    | str
    | BaseElement
    | _HasHtml
    | Iterable["Node"]
    | Callable[[], "Node"]
    | ContextProvider[t.Any]
    | ContextConsumer[t.Any]
)

Attribute: t.TypeAlias = None | bool | str | _HasHtml | _ClassNames

# https://developer.mozilla.org/en-US/docs/Glossary/Doctype
html = HTMLElement("html")

# https://developer.mozilla.org/en-US/docs/Glossary/Void_element
area = VoidElement("area")
base = VoidElement("base")
br = VoidElement("br")
col = VoidElement("col")
embed = VoidElement("embed")
hr = VoidElement("hr")
img = VoidElement("img")
input = VoidElement("input")
link = VoidElement("link")
meta = VoidElement("meta")
param = VoidElement("param")
source = VoidElement("source")
track = VoidElement("track")
wbr = VoidElement("wbr")

# Non-deprecated HTML elements, extracted from
# https://developer.mozilla.org/en-US/docs/Web/HTML/Element
# Located via the inspector with:
# Array.from($0.querySelectorAll('li')).filter(x=>!x.querySelector('.icon-deprecated')).map(x => x.querySelector('code').textContent) # noqa: E501
a = Element("a")
abbr = Element("abbr")
abc = Element("abc")
address = Element("address")
article = Element("article")
aside = Element("aside")
audio = Element("audio")
b = Element("b")
bdi = Element("bdi")
bdo = Element("bdo")
blockquote = Element("blockquote")
body = Element("body")
button = Element("button")
canvas = Element("canvas")
caption = Element("caption")
cite = Element("cite")
code = Element("code")
colgroup = Element("colgroup")
data = Element("data")
datalist = Element("datalist")
dd = Element("dd")
del_ = Element("del_")
details = Element("details")
dfn = Element("dfn")
dialog = Element("dialog")
div = Element("div")
dl = Element("dl")
dt = Element("dt")
em = Element("em")
fieldset = Element("fieldset")
figcaption = Element("figcaption")
figure = Element("figure")
footer = Element("footer")
form = Element("form")
h1 = Element("h1")
h2 = Element("h2")
h3 = Element("h3")
h4 = Element("h4")
h5 = Element("h5")
h6 = Element("h6")
head = Element("head")
header = Element("header")
hgroup = Element("hgroup")
i = Element("i")
iframe = Element("iframe")
ins = Element("ins")
kbd = Element("kbd")
label = Element("label")
legend = Element("legend")
li = Element("li")
main = Element("main")
map = Element("map")
mark = Element("mark")
menu = Element("menu")
meter = Element("meter")
nav = Element("nav")
noscript = Element("noscript")
object = Element("object")
ol = Element("ol")
optgroup = Element("optgroup")
option = Element("option")
output = Element("output")
p = Element("p")
picture = Element("picture")
portal = Element("portal")
pre = Element("pre")
progress = Element("progress")
q = Element("q")
rp = Element("rp")
rt = Element("rt")
ruby = Element("ruby")
s = Element("s")
samp = Element("samp")
script = Element("script")
search = Element("search")
section = Element("section")
select = Element("select")
slot = Element("slot")
small = Element("small")
span = Element("span")
strong = Element("strong")
style = Element("style")
sub = Element("sub")
summary = Element("summary")
sup = Element("sup")
table = Element("table")
tbody = Element("tbody")
td = Element("td")
template = Element("template")
textarea = Element("textarea")
tfoot = Element("tfoot")
th = Element("th")
thead = Element("thead")
time = Element("time")
title = Element("title")
tr = Element("tr")
u = Element("u")
ul = Element("ul")
var = Element("var")
