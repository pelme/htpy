from collections.abc import Generator, Iterator, Sequence
from typing import Protocol, Self, TypeAlias, overload

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
    | Element
    | _HasHtml
    | Sequence["Node"]
    | tuple["Node", ...]
    | Generator["Node", None, None]
)

Attribute: TypeAlias = None | bool | str | _ClassNames

class Element:
    def __init__(self, name: str, attrs: dict[str, Attribute], children: Node): ...
    @overload
    def __call__(self, id_class: str, attrs: dict[str, Attribute], **kwargs: Attribute) -> Self: ...
    @overload
    def __call__(self, id_class: str = "", **kwargs: Attribute) -> Self: ...
    @overload
    def __call__(self, attrs: dict[str, Attribute], **kwargs: Attribute) -> Self: ...
    @overload
    def __call__(self, **kwargs: Attribute) -> Self: ...
    def __iter__(self) -> Iterator[str]: ...

class RegularElement(Element):
    def __getitem__(self, children: Node) -> Self: ...

class VoidElement(Element): ...

class DoctypeElement(RegularElement):
    def __init__(
        self, name: str, attrs: dict[str, Attribute], children: list[Node], *, doctype: str
    ): ...

def __getattr__(name: str) -> RegularElement: ...

# This list should contain all non-deprecated HTML elements
html: DoctypeElement

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
a: RegularElement
abbr: RegularElement
abc: RegularElement
address: RegularElement
article: RegularElement
aside: RegularElement
audio: RegularElement
b: RegularElement
bdi: RegularElement
bdo: RegularElement
blockquote: RegularElement
body: RegularElement
button: RegularElement
canvas: RegularElement
caption: RegularElement
cite: RegularElement
code: RegularElement
colgroup: RegularElement
data: RegularElement
datalist: RegularElement
dd: RegularElement
del_: RegularElement
details: RegularElement
dfn: RegularElement
dialog: RegularElement
div: RegularElement
dl: RegularElement
dt: RegularElement
em: RegularElement
fieldset: RegularElement
figcaption: RegularElement
figure: RegularElement
footer: RegularElement
form: RegularElement
h1: RegularElement
h2: RegularElement
h3: RegularElement
h4: RegularElement
h5: RegularElement
h6: RegularElement
head: RegularElement
header: RegularElement
hgroup: RegularElement
i: RegularElement
iframe: RegularElement
ins: RegularElement
kbd: RegularElement
label: RegularElement
legend: RegularElement
li: RegularElement
main: RegularElement
map: RegularElement
mark: RegularElement
menu: RegularElement
meter: RegularElement
nav: RegularElement
noscript: RegularElement
object: RegularElement
ol: RegularElement
optgroup: RegularElement
option: RegularElement
output: RegularElement
p: RegularElement
picture: RegularElement
portal: RegularElement
pre: RegularElement
progress: RegularElement
q: RegularElement
rp: RegularElement
rt: RegularElement
ruby: RegularElement
s: RegularElement
samp: RegularElement
script: RegularElement
search: RegularElement
section: RegularElement
select: RegularElement
slot: RegularElement
small: RegularElement
span: RegularElement
strong: RegularElement
style: RegularElement
sub: RegularElement
summary: RegularElement
sup: RegularElement
table: RegularElement
tbody: RegularElement
td: RegularElement
template: RegularElement
textarea: RegularElement
tfoot: RegularElement
th: RegularElement
thead: RegularElement
time: RegularElement
title: RegularElement
tr: RegularElement
u: RegularElement
ul: RegularElement
var: RegularElement
