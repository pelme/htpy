from django import forms
from django.http import HttpResponse

from htpy import body, head, html, link, script

from .widgets import ShoelaceInput


class TheForm(forms.Form):
    the_field = forms.CharField(widget=ShoelaceInput)


def widget_view(request):
    form = TheForm()
    return HttpResponse(
        html[
            head[
                link(
                    rel="stylesheet",
                    href="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.14.0/cdn/themes/light.css",
                ),
                script(
                    type="module",
                    src="https://cdn.jsdelivr.net/npm/@shoelace-style/shoelace@2.14.0/cdn/shoelace-autoloader.js",
                ),
            ],
            body[form],
        ]
    )
