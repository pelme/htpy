from __future__ import annotations

import typing as t

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from htpy import Element, h1, p
from htpy.starlette import HtpyResponse

if t.TYPE_CHECKING:
    from starlette.requests import Request


async def html_response(request: Request) -> HTMLResponse:
    return HTMLResponse(h1["Hello, HTMLResponse!"])


async def stuff() -> Element:
    return p["stuff"]


async def htpy_response(request: Request) -> HtpyResponse:
    return HtpyResponse(
        (
            h1["Hello, HtpyResponse!"],
            stuff(),
        )
    )


client = TestClient(
    Starlette(
        debug=True,
        routes=[
            Route("/html-response", html_response),
            Route("/htpy-response", htpy_response),
        ],
    )
)


def test_html_response() -> None:
    response = client.get("/html-response")
    assert response.text == "<h1>Hello, HTMLResponse!</h1>"


def test_htpy_response() -> None:
    response = client.get("/htpy-response")
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert response.text == "<h1>Hello, HtpyResponse!</h1><p>stuff</p>"
