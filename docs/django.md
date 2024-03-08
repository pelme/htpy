# Usage with Django

htpy is not tied to any specific web framework. Nonetheless, htpy works great
when combined with Django. This page contains information and useful techniques
on how to combine htpy and Django.

## Returning a htpy response
htpy elements can be passed directly to `HttpResponse`:

```py title="views.py"
from django.http import HttpResponse
from htpy import div

def my_view(request):
    return HttpResponse(html[body[div["Hi Django!"]]])
```

## Using htpy as part of an existing Django template

htpy elements are marked as "safe" and can be injected directly into Django templates:

```html title="base.html"
<html>
    <head>
        <title>My Django Site</title>
    </head>
    <body>{{ content }}</body>
</html>
```

```py title="views.py"
from django.shortcuts import render

from htpy import h1


def index(request):
    return render(request, "base.html", {"content": h1["Welcome to my site!"]})

```

## Render a Django form with htpy

CSRF token, form widgets and errors can be directly used within htpy elements:

```py title="forms.py"
from django import forms


class MyForm(forms.Form):
    name = forms.CharField()
```

```py title="views.py"
from django.http import HttpResponse

from . import components
from .forms import MyForm


def my_form(request):
    form = MyForm(request.POST or None)
    if form.is_valid():
        return HttpResponse(components.my_form_success())

    return HttpResponse(components.my_form(request, form))
```

```py title="components.py"
from django.template.backends.utils import csrf_input

from htpy import body, button, form, h1, head, html, title


def base(page_title, content):
    return html[head[title[page_title]], body[content]]


def my_form(request, my_form):
    return base(
        "My form",
        form(method="post")[
            csrf_input(request),
            my_form.errors,
            my_form["name"],
            button["Submit!"],
        ],
    )


def my_form_success():
    return base(
        "Success!",
        h1["Success! The form was valid!"],
    )
```


## Implement custom form widgets with htpy

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
