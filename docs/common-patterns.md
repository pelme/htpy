# Common patterns

htpy itself is a library that does not impose any particular structure for your
code. You have the full power of Python
functions, classes and modules at your disposal.

General programming practices on how to structure modules, functions and classes apply to HTML generation with htpy.

This page describes common scenarios and patterns that may help you structure
your own project in a good way.

## File/module structure

It is generally a good idea to keep your HTML pages/components separate from HTTP request handling and "business logic".

In Django, this means that the view function should not directly generate the
HTML.

Using a file named `components.py` can be a good idea. If you have many
components, you may create a `components` package instead.

Your component functions can accept arbitrary argument with the required data:

```py title="views.py"
from django.http import HttpResponse

from . import components

def greeting(request):
    return HttpResponse(components.greeting(
        name=request.GET.get("name", "anonymous"),
    ))
```

```py title="components.py"

def greeting(*, name):
    return html[body[f"hi {name}!"]]
```

## Creating a base layout

A common feature of template languages is to "extend" a base/parent template and specify placeholders. This can be achieved with a `base_layout` function:

```py title="components.py"
import datetime

from htpy import body, div, h1, head, html, p, title


def base_layout(*, page_title=None, extra_head=None, content=None, body_class=None):
    return html[
        head[title[page_title], extra_head],
        body(class_=body_class)[
            content,
            div("#footer")[f"Copyright {datetime.date.today().year} by Foo Inc."],
        ],
    ]


def index():
    return base_layout(
        page_title="Welcome!",
        body_class="green",
        content=[h1["Welcome to my site!"], p["Hello and welcome!"]],
    )


def about():
    return base_layout(
        page_title="About us",
        content=[
            h1["About us"],
            p["We love creating web sites!"],
        ],
    )

```

## UI components

Creating higher level wrappers for common UI components can be a good idea to reduce repitition.

Wrapping [Bootstrap Modal](https://getbootstrap.com/docs/4.0/components/modal/) could be achieved with a function like this:


```py title="Creating wrapper for Bootstrap Modal"
from markupsafe import Markup

from htpy import button, div, h5, span


def bootstrap_modal(*, title, body=None, footer=None):
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
