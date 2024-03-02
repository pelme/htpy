import pytest


@pytest.fixture(scope="session")
def django_env():
    import django
    from django.conf import settings

    settings.configure(TEMPLATES=[{"BACKEND": "django.template.backends.django.DjangoTemplates"}])
    django.setup()
