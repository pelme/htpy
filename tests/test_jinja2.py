from jinja2 import Template

from htpy import li


def test_template_injection() -> None:
    result = Template("<ul>{{ stuff }}</ul>").render(stuff=li["I am safe!"])
    assert result == "<ul><li>I am safe!</li></ul>"
