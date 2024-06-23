# Common Patterns

htpy itself is a library that does not impose any particular structure for your
code. You have the full power of Python
functions, classes and modules at your disposal.

General programming practices on how to structure modules, functions and classes apply to HTML generation with htpy.

This page describes common scenarios and patterns that may help you structure
your own project in a good way.

## File/Module Structure

It is generally a good idea to keep your HTML pages/components separate from HTTP request handling and "business logic".

In Django, this means that the view function should not directly generate the
HTML.

Using a file named `components.py` can be a good idea. If you have many
components, you may create a `components` package instead.

Your component functions can accept arbitrary argument with the required data.
It is a good idea to only use keyword arguments (put a `*` in the argument list
to force keyword arguments):

```py title="views.py"
from django.http import HttpRequest, HttpResponse

from .components import greeting_page

def greeting(request: HttpRequest) -> HttpResponse:
    return HttpResponse(greeting_page(
        name=request.GET.get("name", "anonymous"),
    ))
```

```py title="components.py"
from htpy import html, body, h1

def greeting_page(*, name: str) -> Element:
    return html[body[h1[f"hi {name}!"]]]
```

## Using a Base Layout

A common feature of template languages is to "extend" a base/parent template and specify placeholders. This can be achieved with a `base_layout` function:

```py title="components.py"
import datetime

from htpy import body, div, h1, head, html, p, title, Node, Element


def base_page(*,
    page_title: str | None = None,
    extra_head: Node = None,
    content: Node = None,
    body_class: str | None = None,
) -> Element:
    return html[
        head[title[page_title], extra_head],
        body(class_=body_class)[
            content,
            div("#footer")[f"Copyright {datetime.date.today().year} by Foo Inc."],
        ],
    ]


def index_page() -> Element:
    return base_page(
        page_title="Welcome!",
        body_class="green",
        content=[
            h1["Welcome to my site!"],
            p["Hello and welcome!"],
        ],
    )


def about_page() -> Element:
    return base_page(
        page_title="About us",
        content=[
            h1["About us"],
            p["We love creating web sites!"],
        ],
    )

```

## UI Components

Creating higher level wrappers for common UI components can be a good idea to reduce repetition.

Wrapping [Bootstrap Modal](https://getbootstrap.com/docs/4.0/components/modal/) could be achieved with a function like this:

```py title="Creating wrapper for Bootstrap Modal"
from markupsafe import Markup

from htpy import Element, Node, button, div, h5, span


def bootstrap_modal(*, title: str, body: Node = None, footer: Node = None) -> Element:
    return div(".modal", tabindex="-1", role="dialog")[
        div(".modal-dialog", role="document")[
            div(".modal-content")[
                div(".modal-header")[
                    div(".modal-title")[
                        h5(".modal-title")[title],
                        button(
                            ".close",
                            type="button",
                            data_dismiss="modal",
                            aria_label="Close",
                        )[span(aria_hidden="true")[Markup("&times;")]],
                    ]
                ],
                div(".modal-body")[body],
                footer and div(".modal-footer")[footer],
            ]
        ]
    ]
```

You would then use it like this:

```py
from htpy import button, p

print(
    bootstrap_modal(
        title="Modal title",
        body=p["Modal body text goes here."],
        footer=[
            button(".btn.btn-primary", type="button")["Save changes"],
            button(".btn.btn-secondary", type="button")["Close"],
        ],
    )
)
```
