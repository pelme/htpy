from collections.abc import Callable
from typing import Any

from django.http import HttpRequest
from django.template import Context, TemplateDoesNotExist
from django.utils.module_loading import import_string

from . import Element, render_node


class _HTPYTemplate:
    def __init__(self, func: Callable[[Context | None, HttpRequest | None], Element]) -> None:
        self.func = func

    def render(self, context: Context | None, request: HttpRequest | None) -> str:
        return render_node(self.func(context, request))


class HTPYTemplates:
    def __init__(self, config: Any):
        pass

    def get_template(self, name: str) -> _HTPYTemplate:
        try:
            return _HTPYTemplate(import_string(name))
        except ImportError:
            raise TemplateDoesNotExist(name)
