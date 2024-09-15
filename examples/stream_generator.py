import time
from collections.abc import Iterator

from htpy import Element, li, ul


def numbers() -> Iterator[Element]:
    yield li[1]
    time.sleep(1)
    yield li[2]


def component() -> Element:
    return ul[numbers]


for chunk in component():
    print(chunk)
