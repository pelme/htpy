from __future__ import annotations

from htpy._contexts import Context as Context
from htpy._contexts import ContextConsumer as ContextConsumer
from htpy._contexts import ContextProvider as ContextProvider
from htpy._elements import BaseElement as BaseElement
from htpy._elements import Element as Element
from htpy._elements import HTMLElement as HTMLElement
from htpy._elements import VoidElement as VoidElement
from htpy._fragments import Fragment as Fragment
from htpy._fragments import comment as comment
from htpy._fragments import fragment as fragment
from htpy._legacy_rendering import iter_node as iter_node  # pyright: ignore[reportDeprecated]
from htpy._legacy_rendering import render_node as render_node  # pyright: ignore[reportDeprecated]
from htpy._types import Attribute as Attribute
from htpy._types import Node as Node
from htpy._types import Renderable as Renderable
from htpy._with_children import with_children as with_children

__all__: list[str] = []


def __getattr__(name: str) -> Element:
    from htpy._elements import get_element

    return get_element(name)


# The list of HTML elements is mostly collected from
# https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements
html = HTMLElement("html")

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
source = VoidElement("source")
track = VoidElement("track")
wbr = VoidElement("wbr")

a = Element("a")
abbr = Element("abbr")
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
math = Element("math")
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
svg = Element("svg")
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
video = Element("video")
