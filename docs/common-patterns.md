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

Your component functions can accept arbitrary arguments with the required data.
It is a good idea to only use keyword arguments (put a `*` on the left of the argument list
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
from htpy import Renderable, body, html, h1

def greeting_page(*, name: str) -> Renderable:
    return html[body[h1[f"hi {name}!"]]]
```

## Creating components

A central way of structuring your elements, layouts is by creating components.
The most straightforward way to create a component is to create a function that
accepts arguments to allow customization. htpy requires no special arguments,
decorators or classes to create a component. A component is just a plain Python
function that returns a htpy element.

If you are used to React/JSX, this is similar to React functional components.

!!! note "About Immutability"

    All elements in htpy are immutable, just like in JSX/React. This means that
    it is not possible to change an element once it is created. Instead of
    trying to change an element, you create a "component function" that accepts
    arguments to let you customize your element. You can define the component
    function with as many arguments as you like.

    The immutability of htpy elements is by design. It makes it clearer how
    things are wired together and avoids surprises from changing existing
    elements.

### Using a Base Layout

A common feature of template languages is to "extend" a base/parent template and specify placeholders. This can be achieved with a `base_layout` function:

```py title="components.py"
import datetime

from htpy import Node, Renderable, body, div, h1, head, html, p, title


def base_layout(*,
    page_title: str | None = None,
    extra_head: Node = None,
    content: Node = None,
    body_class: str | None = None,
) -> Renderable:
    return html[
        head[title[page_title], extra_head],
        body(class_=body_class)[
            content,
            div("#footer")[f"Copyright {datetime.date.today().year} by Foo Inc."],
        ],
    ]


def index_page() -> Renderable:
    return base_layout(
        page_title="Welcome!",
        body_class="green",
        content=[
            h1["Welcome to my site!"],
            p["Hello and welcome!"],
        ],
    )


def about_page() -> Renderable:
    return base_layout(
        page_title="About us",
        content=[
            h1["About us"],
            p["We love creating web sites!"],
        ],
    )

```

### UI Components

Creating higher level wrappers for common UI components can be a good idea to reduce repetition.

Wrapping [Bootstrap Modal](https://getbootstrap.com/docs/4.0/components/modal/) could be achieved with a function like this:

```py title="Creating wrapper for Bootstrap Modal"
from markupsafe import Markup

from htpy import Node, Renderable, button, div, h5, span


def bootstrap_modal(*, title: str, body: Node = None, footer: Node = None) -> Renderable:
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

### Components with children

When building their own set of components, some prefer to make their
components accept children nodes in the same way as the HTML elements provided
by htpy.

Making this work correctly in all cases can be tricky, so htpy provides a
decorator called `@with_children`.

With the `@with_children` decorator you can convert a component like this:

```py
from htpy import Node, Renderable

def my_component(*, title: str, children: Node) -> Renderable:
    ...
```

That is used like this:

```py
my_component(title="My title", children=h.div["My content"])
```

Into a component that is defined like this:

```py
from htpy import Node, Renderable, with_children

@with_children
def my_component(children: Node, *, title: str) -> Renderable:
    ...
```

And that is used like this, just like any HTML element:

```py
my_component(title="My title")[h.div["My content"]]
```

You can combine `@with_children` with other decorators, like context
consumers, that also pass extra arguments to the function, but you must make
sure that decorators and arguments are in the right order.

As the innermost decorator is the first to wrap the function, it maps to the
first argument. With multiple decorators, the source code order of the
decorators and arguments are the opposite of each other.

```py
from typing import Literal

from htpy import Context, Node, Renderable, div, h1, with_children

Theme = Literal["light", "dark"]

theme_context: Context[Theme] = Context("theme", default="light")

@with_children
@theme_context.consumer
def my_component(theme: Theme, children: Node, *, extra: str) -> Renderable:
    ...
```
