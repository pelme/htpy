import random
import time
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class Item:
    count: int
    color: str


def generate_items() -> Iterable[Item]:
    for x in range(10):
        yield Item(x + 1, random.choice(["honeydew", "azure", "ivory", "mistyrose", "aliceblue"]))
        time.sleep(1)
