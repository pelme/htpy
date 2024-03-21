import time

from htpy import div, h1


def calculate_magic_number() -> str:
    time.sleep(3)
    return "42"


element = div[
    h1["Welcome to my page"],
    "The magic number is ",
    calculate_magic_number,
]

for chunk in element:
    print(chunk)
