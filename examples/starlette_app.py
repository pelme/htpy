import asyncio
from collections.abc import AsyncIterator

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse, StreamingResponse

import htpy as h

app = Starlette(debug=True)


@app.route("/")
async def homepage(request: Request) -> HTMLResponse:
    return HTMLResponse(
        h.div[
            h.h1["Hello, World!"],
            h.p["This is a simple example of using htpy with Starlette."],
            h.a(href=str(request.url_for("stream")))["Go to the async stream example"],
        ],
    )


async def slow_numbers(minimum: int, maximum: int) -> AsyncIterator[int]:
    for number in range(minimum, maximum + 1):
        yield number
        await asyncio.sleep(0.5)


@app.route("/stream", name="stream")
async def async_stream(request: Request) -> StreamingResponse:
    return StreamingResponse(
        h.div[
            h.h1["Async Stream"],
            h.p["This page is generated asyncronously."],
            h.ul[(h.li[str(num)] async for num in slow_numbers(1, 10))],
        ],
        media_type="text/html",
    )
