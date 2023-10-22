from .safestring import to_html


# Inspired by https://www.npmjs.com/package/classnames
def class_names(value):
    if isinstance(value, list | tuple | set):
        return " ".join(to_html(x) for x in value if x)

    if isinstance(value, dict):
        return " ".join(to_html(k) for k, v in value.items() if v)

    return to_html(value)


_names = {
    "class_": "class",
    "for_": "for",
}


def fixup_attribute_name(name):
    name = _names.get(name, name)
    return name.strip("_").replace("_", "-")


def generate_attrs(raw_attrs):
    for k, v in raw_attrs.items():
        if k == "class":
            v = class_names(v)
        else:
            v = to_html(v)

        yield (k, v)
