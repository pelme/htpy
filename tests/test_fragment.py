import markupsafe

from htpy import Fragment, i, p

from .conftest import RenderFixture


def test_render_direct() -> None:
    assert str(Fragment("Hello ", None, i["World"])) == "Hello <i>World</i>"


def test_render_as_child(render: RenderFixture) -> None:
    assert render(p["Say: ", Fragment("Hello ", None, i["World"]), "!"]) == [
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
    assert render(Fragment(Fragment("Hel", "lo "), "World")) == ["Hel", "lo ", "World"]


def test_render_chunks(render: RenderFixture) -> None:
    assert render(Fragment("Hello ", None, i["World"])) == [
        "Hello ",
        "<i>",
        "World",
        "</i>",
    ]


def test_safe() -> None:
    assert markupsafe.escape(Fragment(i["hi"])) == "<i>hi</i>"


def test_iter() -> None:
    assert list(Fragment("Hello ", None, i["World"])) == ["Hello ", "<i>", "World", "</i>"]
