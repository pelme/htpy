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
