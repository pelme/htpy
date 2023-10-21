from htpy import div, mark_safe


def test_escaping():
    result = str(div("<foo></foo>"))
    assert result == "<div>&lt;foo&gt;&lt;/foo&gt;</div>"


def test_safe_string():
    result = str(div(mark_safe("<foo></foo>")))

    assert result == "<div><foo></foo></div>"
