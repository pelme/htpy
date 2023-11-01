from htpy import div, li, ul


def test_iter() -> None:
    result = div(id="a")["hello"]
    parts = list(result)

    assert parts == ['<div id="a">', "hello", "</div>"]


def test_iter_nested() -> None:
    result = ul[li(id="a")["hi a"], li(id="b")["hi b"]]
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
