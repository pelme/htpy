# Async rendering

htpy fully supports rendering HTML asynchronously. Combined with a async framework such as [Starlette/FastAPI](starlette.md), the entire web request can be processed async and the HTML page can be sent to the client incrementally as soon as it is ready.

# Async components

In addition to regular, [synchronous components](common-patterns.md), components can be defined as an `async def` coroutine. When rendering, htpy will `await` all async components:

```py
from htpy import li
import asyncio

async def get_text():
    return "hi!"

async def my_text() -> Renderable:
    results = await get_text()
    return p[results]
```

## Async iterators

htpy will consume children that are async elements:
```py
from htpy import ul, li

async def my_items() -> AsyncIterator[Renderable]:
    yield li["a"]
    yield li["b"]

def my_list() -> Renderable:
    return ul[my_items()]
```

# Retrieving async content

To retrieve results from async rendering, use the `aiter_chunks()` method. It returns an async iterator that yields the HTML document as bytes.

```py
import asyncio

from htpy import p

my_paragraph = p["hello!"]


async def main():
    async for chunk in my_paragraph.aiter_chunks():
        print(chunk)


asyncio.run(main())

# output:
# <p>
# hello!
# </p>
```

The async iterator returned by `aiter_chunks()` can be passed to your web framework's streaming response class. See the [htpy Starlette docs](starlette.md) for more information how to integrate with Starlette.

!!! warning

    Trying to get the string value of an async renderable like `str(element)` will result an exception:

    ```py
    Traceback (most recent call last):

      File "/Users/andreas/code/htpy/examples/async_in_sync_context.py", line 7, in <module>
        str(div[my_async_component()])
        ~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^

    TypeError: <coroutine object my_async_component at 0x103471010> is not a valid child element.
               Use the `.aiter_chunks()` method to retrieve the content: https://htpy.dev/async/
    ```

    Instead, use `aiter_chunks()`:

    ```py
    async for chunk in div[my_async_component()].aiter_chunks():
        print(chunk)
    ```
