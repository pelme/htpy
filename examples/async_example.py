import asyncio
import random

from htpy import Element, b, div, h1


async def magic_number() -> Element:
    await asyncio.sleep(2)
    return b[f"The Magic Number is: {random.randint(1, 100)}"]


async def my_component() -> Element:
    return div[
        h1["The Magic Number"],
        magic_number(),
    ]


async def main() -> None:
    async for chunk in await my_component():
        print(chunk)


asyncio.run(main())
