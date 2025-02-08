# Streaming of Contents

Internally, htpy is built with generators. Most of the time, you would render
the full page with `str()`, but htpy can also incrementally generate pages
synchronously or asynchronous which can then be streamed to the browser. If your
page uses a database or other services to retrieve data, you can send the
beginning of the page while the rest is being generated. This can improve the
user experience of your site: Typically the `<head>` tag with CSS and JavaScript
files are sent first. The browser will start evaluating scripts and parse CSS
while the page loads. Once the actual data, typically part of the `<body>` or
`<main>` arrives, it can directly be rendered. Typical template based systems
render the entire page at once and then send it to the client, when the server
rendered the full page.

!!! note

    Streaming requires a bit of discipline and care to get right. You need to
    ensure to avoid doing too much work up front and use lazy constructs such as
    generators and callables. Most of the time, rendering the page without
    streaming will be the easiest way to get going. Streaming can give you
    improved user experience from faster pages/rendering.


## Example
This video shows what it looks like in the browser to generate a HTML table with
[Django
StreamingHttpResponse](https://docs.djangoproject.com/en/5.0/ref/request-response/#django.http.StreamingHttpResponse)
([source
code](https://github.com/pelme/htpy/blob/main/examples/djangoproject/stream/views.py)):

This example simulates a (very) slow data source and shows the power of
streaming: The browser loads CSS and gradually shows the contents. By loading
CSS files in the `<head>` tag before dynamic content, the browser can start
working on loading the CSS and styling the page while the server keeps
generating the rest of the page.
<video width="500" controls loop >
  <source src="/assets/stream.webm" type="video/webm">
</video>


## Synchronous streaming

Instead of calling `str()` of an element, you may iterate/loop over it. You will then
get "chunks" of the element as htpy renders the result, as soon as they are ready.

To delay the calculation and allow htpy to incrementally render elements, there
are two types of lazy constructs that can be used:

- Callables/lambdas without any arguments
- Generators

These will be evaluated lazily and

### Callables/lambda

Pass a callable that does not accept any arguments as child. When htpy renders the children, it will call the function to retrieve the result.

This example shows how the page starts rendering and outputs the `<h1>` tag and
then calls `calculate_magic_number`.

```python
import time
from htpy import div, h1

def calculate_magic_number() -> str:
    time.sleep(1)
    print("  (running the complex calculation...)")
    return "42"

element = div[
    h1["Welcome to my page"],
    "The magic number is ",
    calculate_magic_number,
]

# Iterate over the element to get the content incrementally
for chunk in element:
    print(chunk)
```

Output:

```
<div>
<h1>
Welcome to my page
</h1>
The magic number is
42    # <-- Appears after 3 seconds
</div>
```

You may use `lambda` to create a function without arguments to make a an expression lazy:

```py
from htpy import div, h1


def fib(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


print(
    div[
        h1["Fibonacci!"],
        "fib(20)=",
        lambda: fib(20),
    ]
)
# output: <div><h1>Fibonacci!</h1>fib(12)=6765</div>

```

### Generators

Generators can also be used to gradually retrieve output. You may create a
generator function (a function that uses the `yield` keyword) or an generator
comprehension/expression.

```py
import time
from collections.abc import Iterator

from htpy import Element, li, ul


def numbers() -> Iterator[Element]:
    yield li[1]
    time.sleep(1)
    yield li[2]


def component() -> Element:
    return ul[numbers]


for chunk in component():
    print(chunk)
```

Output:

```html
<ul>
<li>
1
</li>
<li>      <|- Appears after 1 second
2         <|
</li>     <|
</ul>
```


## Asynchronous streaming

htpy can be used in fully async mode.

This intended to be used with ASGI/async web frameworks/servers such as
Starlette, Sanic, FastAPI and Django.

Combined with an ORM, database adapter or reading backing data from an async
source, all parts of the stack will be fully async and the client will get the data incrementally.

htpy will `await` any awaitables and iterate over async iterators. Use async iteration on a htpy element or use `aiter_node()` to render any `Node`.


### Starlette, ASGI and uvicorn example

```python
title="starlette_demo.py"
import asyncio
from collections.abc import AsyncIterator

from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import StreamingResponse

from htpy import Element, div, h1, li, p, ul

app = Starlette(debug=True)


@app.route("/")
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

```

Run with [uvicorn](https://www.uvicorn.org/):


```
$ uvicorn starlette_demo:app
```

In the browser, it looks like this:
<video width="500" controls loop >
  <source src="/assets/starlette.webm" type="video/webm">
</video>
