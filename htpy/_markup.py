from html import escape


# Heavily inspired by markupsafe:
# https://github.com/pallets/markupsafe/blob/main/src/markupsafe/__init__.py
class Markup(str):
    __slots__ = ()

    def __new__(cls, obj):
        if hasattr(obj, "__html__"):
            obj = obj.__html__()

        return super().__new__(cls, obj)

    def __html__(self):
        return self


def to_html(obj, *, quote):
    if hasattr(obj, "__html__"):
        return obj.__html__()

    return escape(str(obj), quote=quote)
