from dataclasses import dataclass

import markupsafe
import pytest

import htpy as h

from .conftest import RenderFixture

example_ctx: h.Context[str] = h.Context("example_ctx", default="default!")


@example_ctx.consumer
def example_consumer(value: str) -> str:
    return value


@dataclass(frozen=True)
class RenderableTestCase:
    renderable: h.Renderable
    expected_chunks: list[str]

    def expected_str(self) -> str:
        return "".join(self.expected_chunks)

    def expected_bytes(self) -> bytes:
        return self.expected_str().encode("utf8")


@pytest.fixture(
    params=[
        RenderableTestCase(h.a, ["<a>", "</a>"]),
        RenderableTestCase(h.img, ["<img>"]),
        RenderableTestCase(example_ctx.provider("hi!", "stuff!"), ["stuff!"]),
        RenderableTestCase(example_consumer(), ["default!"]),
        RenderableTestCase(h.fragment["fragment!"], ["fragment!"]),
        # comment() is a Fragment but test it anyways for completeness
        RenderableTestCase(h.comment("comment!"), ["<!-- comment! -->"]),
    ]
)
def case(request: pytest.FixtureRequest) -> RenderableTestCase:
    return request.param  # type: ignore[no-any-return]


def test_str(case: RenderableTestCase) -> None:
    result = str(case.renderable)
    assert isinstance(result, str)
    assert isinstance(result, markupsafe.Markup)
    assert result == case.expected_str()


def test_html(case: RenderableTestCase) -> None:
    result = case.renderable.__html__()
    assert isinstance(result, str)
    assert isinstance(result, markupsafe.Markup)
    assert result == case.expected_str()


def test_encode(case: RenderableTestCase) -> None:
    result = case.renderable.encode()
    assert isinstance(result, bytes)
    assert result == case.expected_bytes()


def test_iter_chunks(case: RenderableTestCase) -> None:
    result = list(case.renderable.iter_chunks())

    # Ensure we get str back, not markup.
    assert type(result[0]) is str

    assert result == case.expected_chunks


def test_aiter_chunks(case: RenderableTestCase, render_async: RenderFixture) -> None:
    result = render_async(case.renderable)
    assert result == case.expected_chunks
