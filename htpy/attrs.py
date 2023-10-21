from .utils import to_html


# Inspired by https://www.npmjs.com/package/classnames
def class_names(value):
    if isinstance(value, list | tuple | set):
        return " ".join(to_html(x) for x in value if x)

    if isinstance(value, dict):
        return " ".join(to_html(k) for k, v in value.items() if v)

    return to_html(value)


def generate_attrs(raw_attrs):
    for raw_key, raw_value in raw_attrs.items():
        if raw_key == "class_":
            yield ("class", class_names(raw_value))
        else:
            yield (raw_key, to_html(raw_value))
