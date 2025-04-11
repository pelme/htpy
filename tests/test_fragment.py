import markupsafe

from htpy import fragment, i, p

from .conftest import RenderFixture


def test_render_direct() -> None:
    assert str(fragment["Hello ", None, i["World"]]) == "Hello <i>World</i>"


def test_render_as_child(render: RenderFixture) -> None:
    assert render(p["Say: ", fragment["Hello ", None, i["World"]], "!"]) == [
        "<p>",
        "Say: ",
        "Hello ",
        "<i>",
        "World",
        "</i>",
        "!",
        "</p>",
    ]


def test_render_nested(render: RenderFixture) -> None:
    assert render(fragment[fragment["Hel", "lo "], "World"]) == ["Hel", "lo ", "World"]


def test_render_chunks(render: RenderFixture) -> None:
    assert render(fragment["Hello ", None, i["World"]]) == [
        "Hello ",
        "<i>",
        "World",
        "</i>",
    ]


def test_safe() -> None:
    assert markupsafe.escape(fragment[i["hi"]]) == "<i>hi</i>"


def test_fragment_iter_chunks() -> None:
    assert list(fragment["Hello ", None, i["World"]].iter_chunks()) == [
        "Hello ",
        "<i>",
        "World",
        "</i>",
    ]
