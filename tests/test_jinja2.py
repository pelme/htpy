from jinja2 import Template
from markupsafe import Markup, escape

from htpy import li, ul


def test_template_injection() -> None:
    result = Template("<ul>{{ stuff }}</ul>").render(stuff=li["I am safe!"])
    assert result == "<ul><li>I am safe!</li></ul>"


def test_Markup() -> None:
    result = ul[Markup("<li>hello</li>")]
    assert str(result) == "<ul><li>hello</li></ul>"


def test_explicit_escape() -> None:
    result = ul[escape("<hi>")]
    assert str(result) == "<ul>&lt;hi&gt;</ul>"
