from __future__ import annotations

import typing as t

from django.template import Context, TemplateDoesNotExist
from django.utils.module_loading import import_string

from . import Element, fragment

if t.TYPE_CHECKING:
    from collections.abc import Callable

    from django.core.checks import Error
    from django.http import HttpRequest


class _HtpyTemplate:
    def __init__(self, func: Callable[[Context | None, HttpRequest | None], Element]) -> None:
        self.func = func

    def render(self, context: Context | None, request: HttpRequest | None) -> str:
        return str(fragment[self.func(context, request)])


class HtpyTemplateBackend:
    def __init__(self, config: t.Any):
        pass

    def get_template(self, name: str) -> _HtpyTemplate:
        try:
            return _HtpyTemplate(import_string(name))
        except ImportError:
            raise TemplateDoesNotExist(name)

    def check(self) -> list[Error]:
        return []
