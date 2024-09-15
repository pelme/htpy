from __future__ import annotations

import dataclasses
import typing as t

import pytest

from htpy import Node, iter_node

if t.TYPE_CHECKING:
    from collections.abc import Callable, Generator


@dataclasses.dataclass(frozen=True)
class Trace:
    description: str


RenderResult: t.TypeAlias = list[str | Trace]
RenderFixture: t.TypeAlias = t.Callable[[Node], RenderResult]
TraceFixture: t.TypeAlias = t.Callable[[str], None]


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
def render_result() -> RenderResult:
    return []


@pytest.fixture
def trace(render_result: RenderResult) -> Callable[[str], None]:
    def func(description: str) -> None:
        render_result.append(Trace(description=description))

    return func


@pytest.fixture
def render(render_result: RenderResult) -> Generator[RenderFixture, None, None]:
    called = False

    def func(node: Node) -> RenderResult:
        nonlocal called

        if called:
            raise AssertionError("render() must only be called once per test")

        called = True
        for chunk in iter_node(node):
            render_result.append(chunk)

        return render_result

    yield func

    if not called:
        raise AssertionError("render() was not called")
