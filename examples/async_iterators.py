from collections.abc import AsyncIterator

from htpy import Element, li, ul


async def my_items() -> AsyncIterator[Element]:
    yield li["a"]
    yield li["b"]


def my_list() -> Element:
    return ul[my_items()]


import asyncio  # noqa: E402

print(my_list())


async def main():
    async for chunk in my_list().aiter_chunks():
        print(chunk)


asyncio.run(main())
