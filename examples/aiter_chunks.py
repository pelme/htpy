import asyncio

from htpy import p

my_paragraph = p["hello!"]


async def main():
    async for chunk in my_paragraph.aiter_chunks():
        print(chunk)


asyncio.run(main())
