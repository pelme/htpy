from django.template import Context, Template

from htpy import li


def test_django_safestring_compat(django_env: None) -> None:
    t = Template("<ul>{{ stuff }}</ul>")
    result = t.render(Context({"stuff": li["I am safe!"]}))

    assert result == "<ul><li>I am safe!</li></ul>"
