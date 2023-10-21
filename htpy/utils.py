from html import escape


def to_html(x):
    if hasattr("x", "__html__"):
        return x.__html__()

    return escape(str(x))
