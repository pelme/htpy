from htpy import div, li, ul


def test_basic() -> None:
    assert str(div("hello")) == "<div>hello</div>"


def test_attribute() -> None:
    assert str(div(id="hello")("hi")) == '<div id="hello">hi</div>'


def test_multiple_children() -> None:
    result = ul(
        li(),
        li(),
    )

    assert str(result) == "<ul><li></li><li></li></ul>"


def test_nested() -> None:
    result = div(id="a")(div(id="b")("inner"))
    assert str(result) == '<div id="a"><div id="b">inner</div></div>'


def test_escape_content() -> None:
    assert str(div('<hello">')) == '<div>&lt;hello"&gt;</div>'


def test_escape_attribute() -> None:
    assert str(div(id='"hello"')) == '<div id="&quot;hello&quot;"></div>'


def test_iter() -> None:
    result = div(id="a")("hello")
    parts = list(result)

    assert parts == ['<div id="a">', "hello", "</div>"]


def test_iter_nested() -> None:
    result = ul(li(id="a")("hi a"), li(id="b")("hi b"))
    parts = list(result)

    assert parts == [
        "<ul>",
        '<li id="a">',
        "hi a",
        "</li>",
        '<li id="b">',
        "hi b",
        "</li>",
        "</ul>",
    ]
