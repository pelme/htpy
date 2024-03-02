from typing import assert_type

from htpy import Markup, div


def test_escaping() -> None:
    result = str(div["<foo></foo>"])
    assert result == "<div>&lt;foo&gt;&lt;/foo&gt;</div>"


def test_Markup() -> None:
    safe_string = Markup("<foo></foo>")
    assert_type(safe_string, Markup)

    result = str(div[safe_string])

    assert result == "<div><foo></foo></div>"
