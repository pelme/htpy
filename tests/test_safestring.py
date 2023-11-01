from typing import assert_type

from htpy import SafeString, div, mark_safe


def test_escaping() -> None:
    result = str(div["<foo></foo>"])
    assert result == "<div>&lt;foo&gt;&lt;/foo&gt;</div>"


def test_mark_safe() -> None:
    safe_string = mark_safe("<foo></foo>")
    assert_type(safe_string, SafeString)

    result = str(div[safe_string])

    assert result == "<div><foo></foo></div>"
