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
