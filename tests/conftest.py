from __future__ import annotations

import typing as t

import pytest

from htpy import Node, iter_node

if t.TYPE_CHECKING:
    from collections.abc import Generator


RenderFixture: t.TypeAlias = t.Callable[[Node], list[str]]


@pytest.fixture(scope="session")
def django_env() -> None:
    import django
    from django.conf import settings

    settings.configure(
        TEMPLATES=[
            {"BACKEND": "django.template.backends.django.DjangoTemplates"},
            {"BACKEND": "htpy.django.HtpyTemplateBackend", "NAME": "htpy"},
        ]
    )
    django.setup()


@pytest.fixture
def render() -> Generator[RenderFixture, None, None]:
    called = False

    def func(node: Node) -> list[str]:
        nonlocal called
        called = True
        return list(iter_node(node))

    yield func

    if not called:
        raise AssertionError("render() was not called")
