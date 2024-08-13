from htpy import comment, div


def test_simple() -> None:
    assert str(div[comment("hi")]) == "<div><!-- hi --></div>"


def test_escape_two_dashes() -> None:
    assert str(div[comment("foo--bar")]) == "<div><!-- foobar --></div>"


def test_escape_three_dashes() -> None:
    assert str(div[comment("foo---bar")]) == "<div><!-- foo-bar --></div>"


def test_escape_four_dashes() -> None:
    assert str(div[comment("foo----bar")]) == "<div><!-- foobar --></div>"
