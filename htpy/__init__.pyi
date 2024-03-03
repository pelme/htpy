from collections.abc import Iterator
from typing import Any, overload

class BaseElement:
    def __init__(self, name: str, attrs: dict[Any, Any], children: list[Any]): ...
    @overload
    def __call__(self, id_class: str, attrs: dict[Any, Any], **kwargs: Any) -> Element: ...
    @overload
    def __call__(self, id_class: str = "", **kwargs: Any) -> Element: ...
    @overload
    def __call__(self, attrs: dict[Any, Any], **kwargs: Any) -> Element: ...
    @overload
    def __call__(self, **kwargs: Any) -> Element: ...
    def __iter__(self) -> Iterator[str]: ...

class Element(BaseElement):
    def __getitem__(self, children: Any) -> Element: ...

class VoidElement(BaseElement): ...

class ElementWithDoctype(Element):
    def __init__(self, name: str, attrs: dict[Any, Any], children: list[Any], *, doctype: str): ...

def __getattr__(name: str) -> Element: ...

# This list should contain all non-deprecated HTML elements
html: ElementWithDoctype

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
