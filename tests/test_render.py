from dataclasses import dataclass

import markupsafe
import pytest

import htpy as h

example_ctx: h.Context[str] = h.Context("example_ctx", default="default!")


@example_ctx.consumer
def example_consumer(value: str) -> str:
    return value


@h.with_children
def example_with_children(
    content: h.Node,
    *,
    title: str = "default!",
) -> h.Renderable:
    return h.div[
        h.h1[title],
        h.p[content],
    ]


@dataclass(frozen=True)
class RenderableTestCase:
    renderable: h.Renderable
    expected_chunks: list[str]

    def expected_str(self) -> str:
        return "".join(self.expected_chunks)

    def expected_bytes(self) -> bytes:
        return self.expected_str().encode("utf8")


cases = [
    RenderableTestCase(h.a, ["<a>", "</a>"]),
    RenderableTestCase(h.img, ["<img>"]),
    RenderableTestCase(example_ctx.provider("hi!", "stuff!"), ["stuff!"]),
    RenderableTestCase(example_consumer(), ["default!"]),
    RenderableTestCase(h.fragment["fragment!"], ["fragment!"]),
    # comment() is a Fragment but test it anyways for completeness
    RenderableTestCase(h.comment("comment!"), ["<!-- comment! -->"]),
    RenderableTestCase(
        example_with_children,
        ["<div>", "<h1>", "default!", "</h1>", "<p>", "</p>", "</div>"],
    ),
    RenderableTestCase(
        example_with_children["children!"],
        ["<div>", "<h1>", "default!", "</h1>", "<p>", "children!", "</p>", "</div>"],
    ),
    RenderableTestCase(
        example_with_children(title="title!"),
        ["<div>", "<h1>", "title!", "</h1>", "<p>", "</p>", "</div>"],
    ),
    RenderableTestCase(
        example_with_children(title="title!")["children!"],
        ["<div>", "<h1>", "title!", "</h1>", "<p>", "children!", "</p>", "</div>"],
    ),
]


@pytest.mark.parametrize("case", cases)
def test_str(case: RenderableTestCase) -> None:
    result = str(case.renderable)
    assert isinstance(result, str)
    assert isinstance(result, markupsafe.Markup)
    assert result == case.expected_str()


@pytest.mark.parametrize("case", cases)
def test_html(case: RenderableTestCase) -> None:
    result = case.renderable.__html__()
    assert isinstance(result, str)
    assert isinstance(result, markupsafe.Markup)
    assert result == case.expected_str()


@pytest.mark.parametrize("case", cases)
def test_encode(case: RenderableTestCase) -> None:
    result = case.renderable.encode()
    assert isinstance(result, bytes)
    assert result == case.expected_bytes()


@pytest.mark.parametrize("case", cases)
def test_iter_chunks(case: RenderableTestCase) -> None:
    result = list(case.renderable.iter_chunks())

    # Ensure we get str back, not markup.
    assert type(result[0]) is str

    assert result == case.expected_chunks
