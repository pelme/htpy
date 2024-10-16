from __future__ import annotations

import asyncio
import dataclasses
import typing as t

import pytest

from htpy import Node, aiter_node, iter_node

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
def render_async(render_result: RenderResult) -> RenderFixture:
    def func(node: Node) -> RenderResult:
        async def run() -> RenderResult:
            async for chunk in aiter_node(node):
                render_result.append(chunk)
            return render_result

        return asyncio.run(run(), debug=True)

    return func


@pytest.fixture(params=["sync", "async"])
def render(
    request: pytest.FixtureRequest,
    render_async: RenderFixture,
    render_result: RenderResult,
) -> Generator[RenderFixture, None, None]:
    called = False

    def render_sync(node: Node) -> RenderResult:
        for chunk in iter_node(node):
            render_result.append(chunk)
        return render_result

    def func(node: Node) -> RenderResult:
        nonlocal called

        if called:
            raise AssertionError("render() must only be called once per test")

        called = True

        if request.param == "sync":
            return render_sync(node)
        else:
            return render_async(node)

    yield func

    if not called:
        raise AssertionError("render() was not called")
