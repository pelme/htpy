import random
import time
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass
class Item:
    count: int
    style: str


def generate_items() -> Iterable[Item]:
    for x in range(10):
        yield Item(x, random.choice(["primary", "secondary", "success", "danger", "warning"]))
        time.sleep(1)
