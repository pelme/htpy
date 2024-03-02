from htpy import Markup, div


def test_escape_children() -> None:
    result = str(div['>"'])
    assert result == '<div>&gt;"</div>'


def test_escape_kwarg_attribute() -> None:
    assert str(div(id='"hello"')) == '<div id="&quot;hello&quot;"></div>'


def test_escape_dict_attribute() -> None:
    assert str(div({'<"': '"hello"'})) == '<div &lt;&quot;="&quot;hello&quot;"></div>'


def test_safe_children() -> None:
    result = str(div[Markup("<hello></hello>")])
    assert result == "<div><hello></hello></div>"


def test_safe_kwarg_attribute() -> None:
    result = str(div(id=Markup("<hi>")))
    assert result == '<div id="<hi>"></div>'


def test_safe_dict_attribute() -> None:
    result = str(div({Markup('<"'): Markup('"hello"')}))
    assert result == '<div <"=""hello""></div>'
