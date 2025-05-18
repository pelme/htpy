from __future__ import annotations

import dataclasses
import functools
import keyword
import typing as t
from collections.abc import Callable, Iterable, Iterator, Mapping

from markupsafe import Markup as _Markup
from markupsafe import escape as _escape

try:
    from typing_extensions import TypedDict, Unpack
except ImportError:
    from typing import TypedDict, Unpack

try:
    from warnings import deprecated  # type: ignore[attr-defined,unused-ignore]
except ImportError:
    from typing_extensions import deprecated

if t.TYPE_CHECKING:
    from types import UnionType

__version__ = "25.4.2"
__all__: list[str] = []

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


def _id_class_names_from_css_str(x: t.Any) -> Mapping[str, Attribute]:
    if not isinstance(x, str):
        raise TypeError(f"id/class strings must be str. got {x}")

    if "#" in x and "." in x and x.find("#") > x.find("."):
        raise ValueError("id (#) must be specified before classes (.)")

    if x[0] not in ".#":
        raise ValueError("id/class strings must start with # or .")

    parts = x.split(".")
    ids = [part.removeprefix("#").strip() for part in parts if part.startswith("#")]
    classes = [part.strip() for part in parts if not part.startswith("#") if part]

    assert len(ids) in (0, 1)

    result: dict[str, Attribute] = {}
    if ids:
        result["id"] = ids[0]

    if classes:
        result["class"] = " ".join(classes)

    return result


def _python_to_html_name(name: str) -> str:
    # Make _hyperscript (https://hyperscript.org/) work smoothly
    if name == "_":
        return "_"

    html_name = name
    name_without_underscore_suffix = name.removesuffix("_")
    if keyword.iskeyword(name_without_underscore_suffix):
        html_name = name_without_underscore_suffix
    html_name = html_name.replace("_", "-")

    return html_name


def _generate_attrs(raw_attrs: Mapping[str, Attribute]) -> Iterable[tuple[str, Attribute]]:
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


def _attrs_string(attrs: Mapping[str, Attribute]) -> str:
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
    node: Node

    @deprecated(  # type: ignore[misc,unused-ignore]
        "iterating over a context provider is deprecated and will be removed in a future release. "
        "Please use the context_provider.iter_chunks() method instead."
    )  # pyright: ignore [reportUntypedFunctionDecorator]
    def __iter__(self) -> Iterator[str]:
        return self.iter_chunks()

    def __str__(self) -> _Markup:
        return _chunks_as_markup(self)

    __html__ = __str__

    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        return _iter_chunks_node(self.node, {**(context or {}), self.context: self.value})  # pyright: ignore [reportUnknownMemberType]

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)


@dataclasses.dataclass(frozen=True)
class ContextConsumer(t.Generic[T]):
    context: Context[T]
    debug_name: str
    func: Callable[[T], Node]

    def __str__(self) -> _Markup:
        return _chunks_as_markup(self)

    __html__ = __str__

    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        context_value = (context or {}).get(self.context, self.context.default)

        if context_value is _NO_DEFAULT:
            raise LookupError(
                f'Context value for "{self.context.name}" does not exist, '  # pyright: ignore
                f"requested by {self.debug_name}()."
            )
        return _iter_chunks_node(self.func(context_value), context)  # pyright: ignore

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)


class _NO_DEFAULT:
    pass


@dataclasses.dataclass(frozen=True)
class Context(t.Generic[T]):
    name: str
    _: dataclasses.KW_ONLY
    default: T | type[_NO_DEFAULT] = _NO_DEFAULT

    def provider(self, value: T, node: Node) -> ContextProvider[T]:
        return ContextProvider(self, value, node)

    def consumer(
        self,
        func: Callable[t.Concatenate[T, P], Node],
    ) -> Callable[P, ContextConsumer[T]]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> ContextConsumer[T]:
            return ContextConsumer(self, func.__name__, lambda value: func(value, *args, **kwargs))

        return wrapper


@deprecated(  # type: ignore[misc,unused-ignore]
    "iter_node is deprecated and will be removed in a future release. "
    "Please use the .iter_chunks() method on elements/fragments instead."
)  # pyright: ignore [reportUntypedFunctionDecorator]
def iter_node(x: Node) -> Iterator[str]:
    return fragment[x].iter_chunks()


def _iter_chunks_node(x: Node, context: Mapping[Context[t.Any], t.Any] | None) -> Iterator[str]:
    while not isinstance(x, BaseElement) and callable(x):
        x = x()

    if x is None:
        return

    if x is True:
        return

    if x is False:
        return

    if hasattr(x, "iter_chunks"):
        yield from x.iter_chunks(context)  # pyright: ignore
    elif isinstance(x, str | _HasHtml):
        yield str(_escape(x))
    elif isinstance(x, int):
        yield str(x)
    elif isinstance(x, Iterable) and not isinstance(x, _KnownInvalidChildren):  # pyright: ignore [reportUnnecessaryIsInstance]
        for child in x:
            yield from _iter_chunks_node(child, context)
    else:
        raise TypeError(f"{x!r} is not a valid child element")


@functools.lru_cache(maxsize=300)
def _get_element(name: str) -> Element:
    if not name.islower():
        raise AttributeError(
            f"{name} is not a valid element name. html elements must have all lowercase names"
        )
    return Element(_python_to_html_name(name))


def __getattr__(name: str) -> Element:
    return _get_element(name)


class BaseElement:
    __slots__ = ("_name", "_attrs", "_children")

    def __init__(self, name: str, attrs_str: str = "", children: Node = None) -> None:
        self._name = name
        self._attrs = attrs_str
        self._children = children

    def __str__(self) -> _Markup:
        return _chunks_as_markup(self)

    __html__ = __str__

    @t.overload
    def __call__(
        self: BaseElementSelf, id_class: str, attrs: Mapping[str, Attribute], /, **kwargs: Unpack[AttrKwargs]
    ) -> BaseElementSelf: ...
    @t.overload
    def __call__(
        self: BaseElementSelf, id_class: str = "", /, **kwargs: Unpack[AttrKwargs]
    ) -> BaseElementSelf: ...
    @t.overload
    def __call__(
        self: BaseElementSelf, attrs: Mapping[str, Attribute], /, **kwargs: Unpack[AttrKwargs]
    ) -> BaseElementSelf: ...
    def __call__(
        self: BaseElementSelf, *args: t.Any, **kwargs: Unpack[AttrKwargs]
    ) -> BaseElementSelf:
        id_class = ""
        attrs: Mapping[str, Attribute] = {}

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
                    **{_python_to_html_name(k): v for k, v in kwargs.items()},
                }
            ),
            self._children,
        )

    @deprecated(  # type: ignore[misc,unused-ignore]
        "iterating over an element is deprecated and will be removed in a future release. "
        "Please use the element.iter_chunks() method instead."
    )  # pyright: ignore [reportUntypedFunctionDecorator]
    def __iter__(self) -> Iterator[str]:
        return self.iter_chunks()

    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        yield f"<{self._name}{self._attrs}>"
        yield from _iter_chunks_node(self._children, context)
        yield f"</{self._name}>"

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)

    # Avoid having Django "call" a htpy element that is injected into a
    # template. Setting do_not_call_in_templates will prevent Django from doing
    # an extra call:
    # https://docs.djangoproject.com/en/5.0/ref/templates/api/#variables-and-lookups
    do_not_call_in_templates = True


def _validate_children(children: t.Any) -> None:
    # Non-lazy iterables:
    # list and tuple are iterables and part of _KnownValidChildren. Since we
    # know they can be consumed multiple times, we validate them recursively now
    # rather than at render time to provide better error messages.
    if isinstance(children, list | tuple):
        for child in children:  # pyright: ignore[reportUnknownVariableType]
            _validate_children(child)
        return

    # bytes, bytearray etc:
    # These are Iterable (part of _KnownValidChildren) but still not
    # useful as a child node.
    if isinstance(children, _KnownInvalidChildren):
        raise TypeError(f"{children!r} is not a valid child element")

    # Element, str, int and all other regular/valid types.
    if isinstance(children, _KnownValidChildren):
        return

    # Arbitrary objects that are not valid children.
    raise TypeError(f"{children!r} is not a valid child element")


class Element(BaseElement):
    def __getitem__(self: ElementSelf, children: Node) -> ElementSelf:
        _validate_children(children)
        return self.__class__(self._name, self._attrs, children)  # pyright: ignore [reportUnknownArgumentType]

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '<{self._name}{self._attrs}>...</{self._name}>'>"


class HTMLElement(Element):
    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        yield "<!doctype html>"
        yield from super().iter_chunks(context)


class VoidElement(BaseElement):
    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        yield f"<{self._name}{self._attrs}>"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '<{self._name}{self._attrs}>'>"


class Fragment:
    """A collection of nodes without a wrapping element."""

    __slots__ = ("_node",)

    def __init__(self) -> None:
        # Make it awkward to instantiate a Fragment directly:
        # Encourage using fragment[x]. That is why it is not possible to set the
        # node directly via the constructor.
        self._node: Node = None

    @deprecated(  # type: ignore[misc,unused-ignore]
        "iterating over a fragment is deprecated and will be removed in a future release. "
        "Please use the fragment.iter_chunks() method instead."
    )  # pyright: ignore [reportUntypedFunctionDecorator]
    def __iter__(self) -> Iterator[str]:
        return self.iter_chunks()

    def __str__(self) -> _Markup:
        return _chunks_as_markup(self)

    __html__ = __str__

    def iter_chunks(self, context: Mapping[Context[t.Any], t.Any] | None = None) -> Iterator[str]:
        return _iter_chunks_node(self._node, context)

    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes:
        return str(self).encode(encoding, errors)


class _FragmentGetter:
    def __getitem__(self, node: Node) -> Fragment:
        result = Fragment()
        result._node = node  # pyright: ignore[reportPrivateUsage]
        return result


fragment = _FragmentGetter()


def _chunks_as_markup(renderable: Renderable) -> _Markup:
    return _Markup("".join(renderable.iter_chunks()))


@deprecated(  # type: ignore[misc,unused-ignore]
    "render_node is deprecated and will be removed in a future release. "
    "Please use fragment instead: https://htpy.dev/usage/#fragments"
)  # pyright: ignore [reportUntypedFunctionDecorator]
def render_node(node: Node) -> _Markup:
    return _Markup(fragment[node])


def comment(text: str) -> Fragment:
    escaped_text = text.replace("--", "")
    return fragment[_Markup(f"<!-- {escaped_text} -->")]


@t.runtime_checkable
class _HasHtml(t.Protocol):
    def __html__(self) -> str: ...


class Renderable(t.Protocol):
    def __str__(self) -> _Markup: ...
    def __html__(self) -> _Markup: ...
    def iter_chunks(
        self, context: Mapping[Context[t.Any], t.Any] | None = None
    ) -> Iterator[str]: ...

    # Allow starlette Response.render to directly render this element without
    # explicitly casting to str:
    # https://github.com/encode/starlette/blob/5ed55c441126687106109a3f5e051176f88cd3e6/starlette/responses.py#L44-L49
    def encode(self, encoding: str = "utf-8", errors: str = "strict") -> bytes: ...


_ClassNamesDict: t.TypeAlias = dict[str, bool]
_ClassNames: t.TypeAlias = Iterable[str | None | bool | _ClassNamesDict] | _ClassNamesDict
Node: t.TypeAlias = (
    Renderable | None | bool | str | int | _HasHtml | Iterable["Node"] | Callable[[], "Node"]
)

_NonClassAttribute: t.TypeAlias = None | bool | str | int | _HasHtml
Attribute: t.TypeAlias = _NonClassAttribute | _ClassNames


class AttrKwargs(TypedDict, total=False, extra_items=_NonClassAttribute):
    # These are the modified attributes to make them valid identifiers
    accept_charset: _NonClassAttribute
    async_: _NonClassAttribute
    class_: Attribute
    for_: _NonClassAttribute
    http_equiv: _NonClassAttribute
    # The rest of the html attributes
    accept: _NonClassAttribute
    accesskey: _NonClassAttribute
    action: _NonClassAttribute
    align: _NonClassAttribute
    alt: _NonClassAttribute
    autocomplete: _NonClassAttribute
    autofocus: _NonClassAttribute
    autoplay: _NonClassAttribute
    bgcolor: _NonClassAttribute
    border: _NonClassAttribute
    charset: _NonClassAttribute
    checked: _NonClassAttribute
    cite: _NonClassAttribute
    color: _NonClassAttribute
    cols: _NonClassAttribute
    colspan: _NonClassAttribute
    content: _NonClassAttribute
    contenteditable: _NonClassAttribute
    controls: _NonClassAttribute
    coords: _NonClassAttribute
    data: _NonClassAttribute
    datetime: _NonClassAttribute
    default: _NonClassAttribute
    defer: _NonClassAttribute
    dir: _NonClassAttribute
    dirname: _NonClassAttribute
    disabled: _NonClassAttribute
    download: _NonClassAttribute
    draggable: _NonClassAttribute
    enctype: _NonClassAttribute
    enterkeyhint: _NonClassAttribute
    form: _NonClassAttribute
    formaction: _NonClassAttribute
    headers: _NonClassAttribute
    height: _NonClassAttribute
    hidden: _NonClassAttribute
    high: _NonClassAttribute
    href: _NonClassAttribute
    hreflang: _NonClassAttribute
    id: _NonClassAttribute
    inert: _NonClassAttribute
    inputmode: _NonClassAttribute
    ismap: _NonClassAttribute
    kind: _NonClassAttribute
    label: _NonClassAttribute
    lang: _NonClassAttribute
    list: _NonClassAttribute
    loop: _NonClassAttribute
    low: _NonClassAttribute
    max: _NonClassAttribute
    maxlength: _NonClassAttribute
    media: _NonClassAttribute
    method: _NonClassAttribute
    min: _NonClassAttribute
    multiple: _NonClassAttribute
    muted: _NonClassAttribute
    name: _NonClassAttribute
    novalidate: _NonClassAttribute
    onabort: _NonClassAttribute
    onafterprint: _NonClassAttribute
    onbeforeprint: _NonClassAttribute
    onbeforeunload: _NonClassAttribute
    onblur: _NonClassAttribute
    oncanplay: _NonClassAttribute
    oncanplaythrough: _NonClassAttribute
    onchange: _NonClassAttribute
    onclick: _NonClassAttribute
    oncontextmenu: _NonClassAttribute
    oncopy: _NonClassAttribute
    oncuechange: _NonClassAttribute
    oncut: _NonClassAttribute
    ondblclick: _NonClassAttribute
    ondrag: _NonClassAttribute
    ondragend: _NonClassAttribute
    ondragenter: _NonClassAttribute
    ondragleave: _NonClassAttribute
    ondragover: _NonClassAttribute
    ondragstart: _NonClassAttribute
    ondrop: _NonClassAttribute
    ondurationchange: _NonClassAttribute
    onemptied: _NonClassAttribute
    onended: _NonClassAttribute
    onerror: _NonClassAttribute
    onfocus: _NonClassAttribute
    onhashchange: _NonClassAttribute
    oninput: _NonClassAttribute
    oninvalid: _NonClassAttribute
    onkeydown: _NonClassAttribute
    onkeypress: _NonClassAttribute
    onkeyup: _NonClassAttribute
    onload: _NonClassAttribute
    onloadeddata: _NonClassAttribute
    onloadedmetadata: _NonClassAttribute
    onloadstart: _NonClassAttribute
    onmousedown: _NonClassAttribute
    onmousemove: _NonClassAttribute
    onmouseout: _NonClassAttribute
    onmouseover: _NonClassAttribute
    onmouseup: _NonClassAttribute
    onmousewheel: _NonClassAttribute
    onoffline: _NonClassAttribute
    ononline: _NonClassAttribute
    onpagehide: _NonClassAttribute
    onpageshow: _NonClassAttribute
    onpaste: _NonClassAttribute
    onpause: _NonClassAttribute
    onplay: _NonClassAttribute
    onplaying: _NonClassAttribute
    onpopstate: _NonClassAttribute
    onprogress: _NonClassAttribute
    onratechange: _NonClassAttribute
    onreset: _NonClassAttribute
    onresize: _NonClassAttribute
    onscroll: _NonClassAttribute
    onsearch: _NonClassAttribute
    onseeked: _NonClassAttribute
    onseeking: _NonClassAttribute
    onselect: _NonClassAttribute
    onstalled: _NonClassAttribute
    onstorage: _NonClassAttribute
    onsubmit: _NonClassAttribute
    onsuspend: _NonClassAttribute
    ontimeupdate: _NonClassAttribute
    ontoggle: _NonClassAttribute
    onunload: _NonClassAttribute
    onvolumechange: _NonClassAttribute
    onwaiting: _NonClassAttribute
    onwheel: _NonClassAttribute
    open: _NonClassAttribute
    optimum: _NonClassAttribute
    pattern: _NonClassAttribute
    placeholder: _NonClassAttribute
    popover: _NonClassAttribute
    popovertarget: _NonClassAttribute
    popovertargetaction: _NonClassAttribute
    poster: _NonClassAttribute
    preload: _NonClassAttribute
    readonly: _NonClassAttribute
    rel: _NonClassAttribute
    required: _NonClassAttribute
    reversed: _NonClassAttribute
    rows: _NonClassAttribute
    rowspan: _NonClassAttribute
    sandbox: _NonClassAttribute
    scope: _NonClassAttribute
    selected: _NonClassAttribute
    shape: _NonClassAttribute
    size: _NonClassAttribute
    sizes: _NonClassAttribute
    span: _NonClassAttribute
    spellcheck: _NonClassAttribute
    src: _NonClassAttribute
    srcdoc: _NonClassAttribute
    srclang: _NonClassAttribute
    srcset: _NonClassAttribute
    start: _NonClassAttribute
    step: _NonClassAttribute
    style: _NonClassAttribute
    tabindex: _NonClassAttribute
    target: _NonClassAttribute
    title: _NonClassAttribute
    translate: _NonClassAttribute
    type: _NonClassAttribute
    usemap: _NonClassAttribute
    value: _NonClassAttribute
    width: _NonClassAttribute
    wrap: _NonClassAttribute


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
del_ = Element("del")
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
_KnownValidChildren: UnionType = (
    None
    | BaseElement
    | ContextProvider  # pyright: ignore [reportMissingTypeArgument]
    | ContextConsumer  # pyright: ignore [reportMissingTypeArgument]
    | str
    | int
    | Fragment
    | _HasHtml
    | Callable
    | Iterable[t.Any]
)
