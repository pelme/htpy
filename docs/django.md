# Usage With Django

htpy is not tied to any specific web framework. Nonetheless, htpy works great
when combined with Django. This page contains information and useful techniques
on how to combine htpy and Django.

## Returning a htpy Response

htpy elements can be passed directly to `HttpResponse`:

```py title="views.py"
from django.http import HttpResponse
from htpy import html, body, div

def my_view(request):
    return HttpResponse(html[body[div["Hi Django!"]]])
```

## Using htpy as Part of an Existing Django Template

htpy elements are marked as "safe" and can be injected directly into Django
templates. This can be useful if you want to start using htpy gradually in an
existing template based Django project:

```html title="base.html"
<html>
    <head>
        <title>My Django Site</title>
    </head>
    <body>
        {{ content }}
    </body>
</html>
```

```py title="views.py"
from django.shortcuts import render

from htpy import h1


def index(request):
    return render(request, "base.html", {
        "content": h1["Welcome to my site!"],
    })
```

## Render a Django Form

CSRF token, form widgets and errors can be directly used within htpy elements:

```py title="forms.py"
from django import forms


class MyForm(forms.Form):
    name = forms.CharField()
```

```py title="views.py"
from django.http import HttpRequest, HttpResponse

from .components import my_form_page, my_form_success_page
from .forms import MyForm


def my_form(request: HttpRequest) -> HttpResponse:
    form = MyForm(request.POST or None)
    if form.is_valid():
        return HttpResponse(my_form_success_page())

    return HttpResponse(my_form_page(request, my_form=form))

```

```py title="components.py"
from django.http import HttpRequest
from django.template.backends.utils import csrf_input

from htpy import Node, Renderable, body, button, form, h1, head, html, title

from .forms import MyForm


def base_page(page_title: str, content: Node) -> Renderable:
    return html[
        head[title[page_title]],
        body[content],
    ]


def my_form_page(request: HttpRequest, *, my_form: MyForm) -> Renderable:
    return base_page(
        "My form",
        form(method="post")[
            csrf_input(request),
            my_form.errors,
            my_form["name"],
            button["Submit!"],
        ],
    )


def my_form_success_page() -> Renderable:
    return base_page(
        "Success!",
        h1["Success! The form was valid!"],
    )
```

## Implement Custom Form Widgets With htpy

You can implement a custom form widget directly with htpy like this:

```py title="widgets.py"
from django.forms import widgets

from htpy import sl_input


class ShoelaceInput(widgets.Widget):
    """
    A form widget using Shoelace's <sl-input> element.
    More info: https://shoelace.style/components/input
    """

    def render(self, name, value, attrs=None, renderer=None):
        return str(sl_input(attrs, name=name, value=value))
```

## The htpy Template Backend

htpy includes a custom template backend. It makes it possible to use htpy
instead of Django templates in places where a template name is required.  This
can be used with generic views or third party applications built to be used with
Django templates.

To enable the htpy template backend, add `htpy.django.HtpyTemplateBackend` to
the `TEMPLATES` setting:

```py
TEMPLATES = [
    ... # Regular Django template configuration goes here
    {"BACKEND": "htpy.django.HtpyTemplateBackend", "NAME": "htpy"}
]
```

In places that expect template names, such as generic views, specify the import
path as a string to a htpy component function:


```python title="pizza/views.py"
from django.views.generic import ListView
from pizza.models import Pizza


class PizzaListView(ListView):
    model = Pizza
    template_name = "pizza.components.pizza_list"
```

In `pizza/components.py`, create a function that accepts two arguments: the
template `Context` (a dictionary with the template variables) and a
`HttpRequest`. It should return the htpy response:

```python title="pizza/components.py"
from htpy import li, ul


def pizza_list(context, request):
    return ul[(li[pizza.name] for pizza in context["object_list"])]
```
