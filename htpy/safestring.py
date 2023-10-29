from html import escape


class mark_safe:
    def __init__(self, value):
        self._value = value

    def __html__(self):
        return self._value


def to_html(obj, *, quote):
    if hasattr(obj, "__html__"):
        return obj.__html__()

    return escape(str(obj), quote=quote)
