from typing import Callable, Iterable, TypeVar
from htpy import Fragment, IgnoredFragment, Node

__all__: list[str] = ["if_", "for_"]


def if_(condition: bool) -> Fragment | IgnoredFragment:
    if condition:
        return Fragment(None)
    else:
        return IgnoredFragment(None)


T = TypeVar("T")


def for_(elements: Iterable[T], callback: Callable[[T], Node]) -> Node:
    children: list[Node] = []
    for e in elements:
        children.append(callback(e))

    return Fragment(children)
