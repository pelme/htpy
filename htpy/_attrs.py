from markupsafe import Markup, escape


# Inspired by https://www.npmjs.com/package/classnames
def class_names(value):
    if isinstance(value, list | tuple | set):
        return Markup(" ").join(
            result for x in value if (result := _dict_class_names(x) if isinstance(x, dict) else x)
        )

    if isinstance(value, dict):
        return _dict_class_names(value)

    return escape(value)


def _dict_class_names(value):
    return Markup(" ").join(k for k, v in value.items() if v)


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
            yield ("class", class_names(value))

        elif value in (False, None):
            continue

        elif value is True:
            yield escape(key), True

        else:
            yield escape(key), escape(value)
