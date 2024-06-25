from markupsafe import Markup

from htpy import render_orphans, tr


def test_render_orphan() -> None:
    result = render_orphans([tr["a"], tr["b"]])

    assert isinstance(result, Markup)
    assert result == "<tr>a</tr><tr>b</tr>"
