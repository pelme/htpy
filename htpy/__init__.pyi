from collections.abc import Callable, Generator, Iterator, Sequence
from typing import Protocol, TypeAlias, overload

class _HasHtml(Protocol):
    def __html__(self) -> str: ...

_ClassNamesDict: TypeAlias = dict[str, bool]
_ClassNames: TypeAlias = (
    list[str | None | bool | _ClassNamesDict]
    | tuple[str | None | bool | _ClassNamesDict, ...]
    | _ClassNamesDict
)
Node: TypeAlias = (
    None
    | str
    | BaseElement
    | _HasHtml
    | Sequence["Node"]
    | tuple["Node", ...]
    | Generator["Node", None, None]
    | Callable[[], "Node"]
)

Attribute: TypeAlias = None | bool | str | _HasHtml | _ClassNames

class BaseElement:
    def __init__(self, name: str, attrs: dict[str, Attribute], children: Node): ...
    @overload
    def __call__(
        self, id_class: str, attrs: dict[str, Attribute], **kwargs: Attribute
    ) -> Element: ...
    @overload
    def __call__(self, id_class: str = "", **kwargs: Attribute) -> Element: ...
    @overload
    def __call__(self, attrs: dict[str, Attribute], **kwargs: Attribute) -> Element: ...
    @overload
    def __call__(self, **kwargs: Attribute) -> Element: ...
    def __iter__(self) -> Iterator[str]: ...

class Element(BaseElement):
    def __getitem__(self, children: Node) -> Element: ...

class VoidElement(BaseElement): ...
class HTMLElement(Element): ...

def __getattr__(name: str) -> Element: ...

# This list should contain all non-deprecated HTML elements
html: HTMLElement

area: VoidElement
base: VoidElement
br: VoidElement
col: VoidElement
embed: VoidElement
hr: VoidElement
img: VoidElement
input: VoidElement
link: VoidElement
meta: VoidElement
source: VoidElement
track: VoidElement
wbr: VoidElement

# Non-deprecated HTML elements, extracted from
# https://developer.mozilla.org/en-US/docs/Web/HTML/Element
# Located via the inspector with:
# Array.from($0.querySelectorAll('li')).filter(x=>!x.querySelector('.icon-deprecated')).map(x => x.querySelector('code').textContent) # noqa: E501
a: Element
abbr: Element
abc: Element
address: Element
article: Element
aside: Element
audio: Element
b: Element
bdi: Element
bdo: Element
blockquote: Element
body: Element
button: Element
canvas: Element
caption: Element
cite: Element
code: Element
colgroup: Element
data: Element
datalist: Element
dd: Element
del_: Element
details: Element
dfn: Element
dialog: Element
div: Element
dl: Element
dt: Element
em: Element
fieldset: Element
figcaption: Element
figure: Element
footer: Element
form: Element
h1: Element
h2: Element
h3: Element
h4: Element
h5: Element
h6: Element
head: Element
header: Element
hgroup: Element
i: Element
iframe: Element
ins: Element
kbd: Element
label: Element
legend: Element
li: Element
main: Element
map: Element
mark: Element
menu: Element
meter: Element
nav: Element
noscript: Element
object: Element
ol: Element
optgroup: Element
option: Element
output: Element
p: Element
picture: Element
portal: Element
pre: Element
progress: Element
q: Element
rp: Element
rt: Element
ruby: Element
s: Element
samp: Element
script: Element
search: Element
section: Element
select: Element
slot: Element
small: Element
span: Element
strong: Element
style: Element
sub: Element
summary: Element
sup: Element
table: Element
tbody: Element
td: Element
template: Element
textarea: Element
tfoot: Element
th: Element
thead: Element
time: Element
title: Element
tr: Element
u: Element
ul: Element
var: Element
