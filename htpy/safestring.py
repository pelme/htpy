from html import escape


class mark_safe:
    def __init__(self, value):
        self._value = value

    def __html__(self):
        return self._value


def to_html(x):
    if hasattr(x, "__html__"):
        return x.__html__()

    return escape(str(x))
