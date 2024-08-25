from __future__ import annotations

import typing as t

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.routing import Route
from starlette.testclient import TestClient

from htpy import h1

if t.TYPE_CHECKING:
    from starlette.requests import Request


async def html_response(request: Request) -> HTMLResponse:
    return HTMLResponse(h1["Hello, HTMLResponse!"])


client = TestClient(
    Starlette(
        debug=True,
        routes=[
            Route("/html-response", html_response),
        ],
    )
)


def test_html_response() -> None:
    response = client.get("/html-response")
    assert response.content == b"<h1>Hello, HTMLResponse!</h1>"
