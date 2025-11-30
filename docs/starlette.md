# Usage with Starlette/FastAPI

htpy can be used with Starlette to generate HTML. Since FastAPI is built upon Starlette, htpy can also be used with FastAPI.

htpy supports full async rendering of all components. See [async rendering](async.md) for more information.

To return HTML contents, use the `HtpyResponse` class:

```py
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route

from htpy import Element, h1
from htpy.starlette import HtpyResponse


async def index_component() -> Element:
    return h1["Hi Starlette!"]


async def index(request: Request) -> HtpyResponse:
    return HtpyResponse(index_component())


app = Starlette(
    routes=[
        Route("/", index),
    ]
)
```
