from __future__ import annotations

import typing as t

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from htpy import Element, h1, li, ul
from htpy.starlette import HtpyResponse

if t.TYPE_CHECKING:
    from starlette.requests import Request


async def html_response(request: Request) -> HTMLResponse:
    return HTMLResponse(h1["Hello, HTMLResponse!"])


async def number_item(number: int) -> Element:
    return li[number]


async def number_list() -> Element:
    return ul[((await number_item(n)) for n in range(3))]


async def stream_response(request: Request) -> HtpyResponse:
    return HtpyResponse(await number_list())


app = Starlette(
    debug=True,
    routes=[
        Route("/html-response", html_response),
        Route("/stream-response", stream_response),
    ],
)
client = TestClient(app)


def test_html_response() -> None:
    response = client.get("/html-response")
    assert response.content == b"<h1>Hello, HTMLResponse!</h1>"


def test_streaming_response() -> None:
    response = client.get("/stream-response")
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.content == b"<ul><li>0</li><li>1</li><li>2</li></ul>"
