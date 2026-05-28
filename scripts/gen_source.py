import json
import keyword
from collections.abc import Sequence
from textwrap import dedent

from htpy.html2htpy import RuffFormatter


def escape_attr(attr: str) -> str:
    attr = attr.replace("-", "_")
    if keyword.iskeyword(attr):
        return attr + "_"
    return attr


def gen_element(name: str, void: bool, attrs: Sequence[str]):
    attr_kwargs = " ".join(f"{escape_attr(attr)}: Attribute = None," for attr in attrs)
    source = f"""\
    class {name.title()}({"VoidElement" if void else "Element"}):
        def __init__(self, attrs_str: str = "", children: Node = None) -> None:
            super().__init__('{name}', attrs_str, children)

        @t.overload
        def __call__(
                self: ElementSelf,
                id_class: str,
                /,
                *attrs: Mapping[str, Attribute],
                {attr_kwargs}
                **kwargs: Attribute,
        ) -> ElementSelf: ...
        @t.overload
        def __call__(
                self: ElementSelf,
                /,
                *attrs: Mapping[str, Attribute],
                {attr_kwargs}
                **kwargs: Attribute,
        ) -> ElementSelf: ...
        def __call__(self: ElementSelf, /, *args: t.Any, **kwargs: t.Any) -> ElementSelf:
            super().__call__(*args, **kwargs)
"""
    return dedent(source)


if __name__ == "__main__":
    with open("html_spec.json") as f:
        spec = json.load(f)
    global_attrs = spec["global_attributes"]
    elements = spec["elements"]
    output = dedent("""\
    import typing as t
    from typing import Mapping
    from htpy import Element, VoidElement, Attribute, Node
    ElementSelf = t.TypeVar("ElementSelf", bound="Element")
    """)
    for element, info in elements.items():
        all_attrs = [*global_attrs]
        for attr in info["attributes"]:
            if attr not in all_attrs:
                all_attrs.append(attr)
        output += gen_element(element, info["void"], all_attrs)
    formatter = RuffFormatter()
    output = formatter.format(output)
    with open("elements.py", "w") as f:
        f.write(output)
