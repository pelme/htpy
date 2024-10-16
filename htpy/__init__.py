from __future__ import annotations

__version__ = "24.9.1"
__all__: list[str] = []

import dataclasses
import functools
import typing as t
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Generator,
    Iterable,
    Iterator,
)

from markupsafe import Markup as _Markup
from markupsafe import escape as _escape

if t.TYPE_CHECKING:
    from types import UnionType

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
        raise TypeError(f"id/class strings must be str. got {x}")

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
            raise TypeError("Attribute key must be a string")

        if value is False or value is None:
            continue

        if key == "class":
            if result := _class_names(value):
                yield ("class", result)

        elif value is True:
            yield _force_escape(key), True

        else:
            if not isinstance(value, str | int | _HasHtml):
                raise TypeError(f"Attribute value must be a string or an integer , got {value!r}")

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

    def __aiter__(self) -> AsyncIterator[str]:
        return aiter_node(self)

    def __str__(self) -> str:
        return render_node(self)


@dataclasses.dataclass(frozen=True)
class ContextConsumer(t.Generic[T]):
    context: Context[T]
    debug_name: str
    func: Callable[[T], Node]


def _is_noop_node(x: Node) -> bool:
    return x is None or x is True or x is False


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

    if _is_noop_node(x):
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
    elif isinstance(x, int):
        yield str(x)
    elif isinstance(x, Iterable) and not isinstance(x, _KnownInvalidChildren):  # pyright: ignore [reportUnnecessaryIsInstance]
        for child in x:
            yield from _iter_node_context(child, context_dict)
    elif isinstance(x, Awaitable | AsyncIterable):  # pyright: ignore[reportUnnecessaryIsInstance]
        raise ValueError(
            f"{x!r} is not a valid child element. "
            "Use async iteration to retrieve element content: https://htpy.dev/streaming/"
        )
    else:
        raise TypeError(f"{x!r} is not a valid child element")


def aiter_node(x: Node) -> AsyncIterator[str]:
    return _aiter_node_context(x, {})


async def _aiter_node_context(
    x: Node, context_dict: dict[Context[t.Any], t.Any]
) -> AsyncIterator[str]:
    while True:
        if isinstance(x, Awaitable):
            x = await x
            continue

        if not isinstance(x, BaseElement) and callable(x):
            x = x()
            continue

        break

    if _is_noop_node(x):
        return

    if isinstance(x, BaseElement):
        async for child in x._aiter_context(context_dict):  # pyright: ignore [reportPrivateUsage]
            yield child
    elif isinstance(x, ContextProvider):
        async for chunk in _aiter_node_context(
            x.func(),
            {**context_dict, x.context: x.value},  # pyright: ignore [reportUnknownMemberType]
        ):
            yield chunk

    elif isinstance(x, ContextConsumer):
        context_value = context_dict.get(x.context, x.context.default)
        if context_value is _NO_DEFAULT:
            raise LookupError(
                f'Context value for "{x.context.name}" does not exist, '
                f"requested by {x.debug_name}()."
            )
        async for chunk in _aiter_node_context(x.func(context_value), context_dict):
            yield chunk

    elif isinstance(x, str | _HasHtml):
        yield str(_escape(x))
    elif isinstance(x, int):
        yield str(x)
    elif isinstance(x, Iterable) and not isinstance(x, _KnownInvalidChildren):  # pyright: ignore [reportUnnecessaryIsInstance]
        for child in x:  # type: ignore[assignment]
            async for chunk in _aiter_node_context(child, context_dict):
                yield chunk
    elif isinstance(x, AsyncIterable):  # pyright: ignore[reportUnnecessaryIsInstance]
        async for child in x:  # type: ignore[assignment]
            async for chunk in _aiter_node_context(child, context_dict):  # pyright: ignore[reportUnknownArgumentType]
                yield chunk
    else:
        raise TypeError(f"{x!r} is not a valid child element")


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

    def __init__(self, name: str, attrs_str: str = "", children: Node = None) -> None:
        self._name = name
        self._attrs = attrs_str
        self._children = children

    def __str__(self) -> _Markup:
        return _Markup("".join(self))

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
            _attrs_string(
                {
                    **(_id_class_names_from_css_str(id_class) if id_class else {}),
                    **attrs,
                    **{_kwarg_attribute_name(k): v for k, v in kwargs.items()},
                }
            ),
            self._children,
        )

    async def _aiter_context(self, context: dict[Context[t.Any], t.Any]) -> AsyncIterator[str]:
        yield f"<{self._name}{self._attrs}>"
        async for x in _aiter_node_context(self._children, context):
            yield x
        yield f"</{self._name}>"

    def __aiter__(self) -> AsyncIterator[str]:
        return self._aiter_context({})

    def __iter__(self) -> Iterator[str]:
        return self._iter_context({})

    def _iter_context(self, ctx: dict[Context[t.Any], t.Any]) -> Iterator[str]:
        yield f"<{self._name}{self._attrs}>"
        yield from _iter_node_context(self._children, ctx)
        yield f"</{self._name}>"

    # Allow starlette Response.render to directly render this element without
    # explicitly casting to str:
    # https://github.com/encode/starlette/blob/5ed55c441126687106109a3f5e051176f88cd3e6/starlette/responses.py#L44-L49
    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)

    # Avoid having Django "call" a htpy element that is injected into a
    # template. Setting do_not_call_in_templates will prevent Django from doing
    # an extra call:
    # https://docs.djangoproject.com/en/5.0/ref/templates/api/#variables-and-lookups
    do_not_call_in_templates = True


def _validate_children(children: t.Any) -> None:
    if isinstance(children, _KnownValidChildren):
        return

    if isinstance(children, Iterable) and not isinstance(children, _KnownInvalidChildren):
        for child in children:  # pyright: ignore [reportUnknownVariableType]
            _validate_children(child)
        return

    raise TypeError(f"{children!r} is not a valid child element")


class Element(BaseElement):
    def __getitem__(self: ElementSelf, children: Node) -> ElementSelf:
        _validate_children(children)
        return self.__class__(self._name, self._attrs, children)  # pyright: ignore [reportUnknownArgumentType]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '<{self._name}{self._attrs}>...</{self._name}>'>"


class HTMLElement(Element):
    def _iter_context(self, ctx: dict[Context[t.Any], t.Any]) -> Iterator[str]:
        yield "<!doctype html>"
        yield from super()._iter_context(ctx)

    async def _aiter_context(self, context: dict[Context[t.Any], t.Any]) -> AsyncIterator[str]:
        yield "<!doctype html>"
        async for x in super()._aiter_context(context):
            yield x


class VoidElement(BaseElement):
    async def _aiter_context(self, context: dict[Context[t.Any], t.Any]) -> AsyncIterator[str]:
        yield f"<{self._name}{self._attrs}>"

    def _iter_context(self, ctx: dict[Context[t.Any], t.Any]) -> Iterator[str]:
        yield f"<{self._name}{self._attrs}>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '<{self._name}{self._attrs}>'>"


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
    | int
    | BaseElement
    | _HasHtml
    | Iterable["Node"]
    | Callable[[], "Node"]
    | ContextProvider[t.Any]
    | ContextConsumer[t.Any]
    | AsyncIterable["Node"]
    | Awaitable["Node"]
)

Attribute: t.TypeAlias = None | bool | str | int | _HasHtml | _ClassNames

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


_KnownInvalidChildren: UnionType = bytes | bytearray | memoryview

_KnownValidChildren: UnionType = (  # pyright: ignore [reportUnknownVariableType]
    None
    | BaseElement
    | AsyncIterable  # pyright: ignore [reportMissingTypeArgument]
    | Awaitable  # pyright: ignore [reportMissingTypeArgument]
    | ContextProvider  # pyright: ignore [reportMissingTypeArgument]
    | ContextConsumer  # pyright: ignore [reportMissingTypeArgument]
    | Callable  # pyright: ignore [reportMissingTypeArgument]
    | str
    | int
    | Generator  # pyright: ignore [reportMissingTypeArgument]
    | _HasHtml
)
