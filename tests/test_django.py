from django.template import Context, Template
from django.utils.html import escape as django__escape
from django.utils.safestring import SafeString as django__SafeString

from htpy import li, ul


def test_template_injection(django_env: None) -> None:
    t = Template("<ul>{{ stuff }}</ul>")
    result = t.render(Context({"stuff": li["I am safe!"]}))

    assert result == "<ul><li>I am safe!</li></ul>"


def test_SafeString(django_env: None) -> None:
    result = ul[django__SafeString("<li>hello</li>")]
    assert str(result) == "<ul><li>hello</li></ul>"


def test_explicit_escape(django_env: None) -> None:
    result = ul[django__escape("<hello>")]
    assert str(result) == "<ul>&lt;hello&gt;</ul>"
