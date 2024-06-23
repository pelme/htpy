# Streaming of Contents

Internally, htpy is built with generators. Most of the time, you would render
the full page with `str()`, but htpy can also incrementally generate pages which
can then be streamed to the browser. If your page uses a database or other
services to retrieve data, you can sending the first part of the page to the
client while the page is being generated.

!!! note

    Streaming requires a bit of discipline and care to get right. You need to
    ensure to avoid doing too much work up front and use lazy constructs such as
    generators and callables. Most of the time, rendering the page without
    streaming will be the easiest way to get going. Streaming can give you
    improved user experience from faster pages/rendering.

This video shows what it looks like in the browser to generate a HTML table with [Django StreamingHttpResponse](https://docs.djangoproject.com/en/5.0/ref/request-response/#django.http.StreamingHttpResponse) ([source code](https://github.com/pelme/htpy/blob/main/examples/djangoproject/stream/views.py)):
<video width="500" controls loop >

  <source src="/assets/stream.webm" type="video/webm">
</video>

This example simulates a (very) slow fetch of data and shows the power of
streaming: The browser loads CSS and gradually shows the contents. By loading
CSS files in the `<head>` tag before dynamic content, the browser can start
working on loading the CSS and styling the page while the server keeps
generating the rest of the page.

## Using Generators and Callables as Children

Django's querysets are [lazily
evaluated](https://docs.djangoproject.com/en/5.0/topics/db/queries/#querysets-are-lazy).
They will not execute a database query before their value is actually needed.

This example shows how this property of Django querysets can be used to create a
page that streams objects:

```python
from django.http import StreamingHttpResponse
from htpy import ul, li

from myapp.models import Article

def article_list(request):
    return StreamingHttpResponse(ul[
        (li[article.title] for article in Article.objects.all())
    ])
```

## Using Callables to Delay Evalutation

Pass a callable that does not accept any arguements as child to delay the
evaluation.

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
        lambda: str(fib(20)),
    ]
)
# output: <div><h1>Fibonacci!</h1>fib(12)=6765</div>

```
