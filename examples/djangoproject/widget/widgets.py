from django.forms import widgets

from htpy import sl_input


class ShoelaceInput(widgets.Widget):
    """
    A form widget using Shoelace's <sl-input> element.
    More info: https://shoelace.style/components/input
    """

    def render(self, name, value, attrs=None, renderer=None):
        return str(sl_input(attrs, name=name, value=value))
