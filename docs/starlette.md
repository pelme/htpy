# Usage with Starlette

htpy can be used with Starlette to generate HTML. Since FastAPI is built upon Starlette, htpy can also be used with FastAPI.

To return HTML contents, pass a htpy element to Starlette's `HTMLResponse`:

```py
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import HTMLResponse
from starlette.routing import Route

from htpy import h1


async def index(request: Request) -> HTMLResponse:
    return HTMLResponse(h1["Hi Starlette!"])


app = Starlette(routes=[Route("/", index)])
```
