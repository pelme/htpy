from __future__ import annotations

import asyncio
import dataclasses
import typing as t

import pytest

import htpy as h

if t.TYPE_CHECKING:
    from collections.abc import Callable, Generator


@dataclasses.dataclass(frozen=True)
class Trace:
    description: str


RenderResult: t.TypeAlias = list[str | Trace]
RenderFixture: t.TypeAlias = t.Callable[[h.Renderable], RenderResult]
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
def render_async(render_result: RenderResult) -> Callable[[h.Renderable], RenderResult]:
    def func(renderable: h.Renderable) -> RenderResult:
        async def run() -> RenderResult:
            async for chunk in renderable.aiter_chunks():
                render_result.append(chunk)
            return render_result

        return asyncio.run(run(), debug=True)

    return func


@pytest.fixture(params=["sync", "async"])
def render(
    request: pytest.FixtureRequest,
    render_result: RenderResult,
    render_async: RenderFixture,
) -> Generator[RenderFixture, None, None]:
    called = False

    def func(renderable: h.Renderable) -> RenderResult:
        nonlocal called

        if called:
            raise AssertionError("render() must only be called once per test")

        called = True

        if request.param == "sync":
            for chunk in renderable.iter_chunks():
                render_result.append(chunk)

            return render_result
        elif request.param == "async":
            return render_async(renderable)
        else:
            raise AssertionError(request.param)

    yield func

    if not called:
        raise AssertionError("render() was not called")
