from ._markup import Markup, to_html


# Inspired by https://www.npmjs.com/package/classnames
def class_names(value):
    if isinstance(value, list | tuple | set):
        return Markup(" ".join(to_html(x, quote=True) for x in value if x))

    if isinstance(value, dict):
        return Markup(" ".join(to_html(k, quote=True) for k, v in value.items() if v))

    return Markup(to_html(value, quote=True))


def id_classnames_from_css_str(x):
    if not isinstance(x, str):
        raise ValueError(f"id/class strings must be str. got {x}")

    if "#" in x and "." in x and x.find("#") > x.find("."):
        raise ValueError("id (#) must be specified before classes (.)")

    if x[0] not in ".#":
        raise ValueError("id/class strings must start with # or .")

    parts = x.split(".")
    ids = [part.removeprefix("#") for part in parts if part.startswith("#")]
    classes = [part for part in parts if not part.startswith("#") if part]

    assert len(ids) in (0, 1)

    result = {}
    if ids:
        result["id"] = ids[0]

    if classes:
        result["class"] = " ".join(classes)

    return result


def kwarg_attribute_name(name):
    # Make _hyperscript (https://hyperscript.org/) work smoothly
    if name == "_":
        return "_"

    return name.removesuffix("_").replace("_", "-")


def generate_attrs(raw_attrs):
    for key, value in raw_attrs.items():
        if key == "class":
            value = class_names(value)

        if value is False:
            continue

        elif value is not True:
            value = to_html(value, quote=True)

        yield to_html(key, quote=True), value
