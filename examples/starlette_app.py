import asyncio
from collections.abc import AsyncIterator

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import StreamingResponse
from starlette.routing import Route

from htpy import Element, div, h1, li, p, ul


async def index(request: Request) -> StreamingResponse:
    return StreamingResponse(await index_page(), media_type="text/html")


async def index_page() -> Element:
    return div[
        h1["Starlette Async example"],
        p["This page is generated asynchronously using Starlette and ASGI."],
        ul[(li[str(num)] async for num in slow_numbers(1, 10))],
    ]


async def slow_numbers(minimum: int, maximum: int) -> AsyncIterator[int]:
    for number in range(minimum, maximum + 1):
        yield number
        await asyncio.sleep(0.5)


app = Starlette(
    debug=True,
    routes=[
        Route("/", index),
    ],
)
