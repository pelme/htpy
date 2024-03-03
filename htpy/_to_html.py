from html import escape


def to_html(obj, *, quote):
    if hasattr(obj, "__html__"):
        return obj.__html__()

    return escape(str(obj), quote=quote)
