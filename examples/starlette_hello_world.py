from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Route

from htpy import Renderable, h1
from htpy.starlette import HtpyResponse


async def index_component() -> Renderable:
    return h1["Hi Starlette!"]


async def index(request: Request) -> HtpyResponse:
    return HtpyResponse(index_component())


app = Starlette(
    routes=[
        Route("/", index),
    ]
)
