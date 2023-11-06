from html import escape


class SafeString(str):
    def __html__(self):
        return self


def mark_safe(obj):
    if hasattr(obj, "__html__"):
        return obj

    return SafeString(obj)


def to_html(obj, *, quote):
    if hasattr(obj, "__html__"):
        return obj.__html__()

    return escape(str(obj), quote=quote)
