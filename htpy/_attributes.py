from __future__ import annotations

import typing as t
from collections.abc import Iterable

import markupsafe

from htpy._types import HasHtml

if t.TYPE_CHECKING:
    from collections.abc import Mapping

    from htpy._types import Attribute


def _force_escape(value: t.Any) -> str:
    return markupsafe.escape(str(value))


# Inspired by https://www.npmjs.com/package/classnames
def _class_names(items: t.Any) -> t.Any:
    if isinstance(items, str):
        return _force_escape(items)

    if isinstance(items, dict) or not isinstance(items, Iterable):
        items = [items]

    result = list(_class_names_for_items(items))
    if not result:
        return False

    return " ".join(_force_escape(class_name) for class_name in result)


def _class_names_for_items(items: t.Any) -> t.Any:
    for item in items:
        if isinstance(item, dict):
            for k, v in item.items():  # pyright: ignore [reportUnknownVariableType]
                if v:
                    yield k
        else:
            if item:
                yield item


def id_class_names_from_css_str(x: t.Any) -> Mapping[str, Attribute]:
    if not isinstance(x, str):
        raise TypeError(f"id/class strings must be str. got {x}")

    if "#" in x and "." in x and x.find("#") > x.find("."):
        raise ValueError("id (#) must be specified before classes (.)")

    if x[0] not in ".#":
        raise ValueError("id/class strings must start with # or .")

    parts = x.split(".")
    ids = [part.removeprefix("#").strip() for part in parts if part.startswith("#")]
    classes = [part.strip() for part in parts if not part.startswith("#") if part]

    assert len(ids) in (0, 1)

    result: dict[str, Attribute] = {}
    if ids:
        result["id"] = ids[0]

    if classes:
        result["class"] = " ".join(classes)

    return result


def _generate_attrs(raw_attrs: Mapping[str, Attribute]) -> Iterable[tuple[str, Attribute]]:
    for key, value in raw_attrs.items():
        if not isinstance(key, str):  # pyright: ignore [reportUnnecessaryIsInstance]
            raise TypeError("Attribute key must be a string")

        if value is False or value is None:
            continue

        if key == "class":
            if result := _class_names(value):
                yield ("class", result)

        elif value is True:
            yield _force_escape(key), True

        else:
            if not isinstance(value, str | int | HasHtml):
                raise TypeError(f"Attribute value must be a string or an integer , got {value!r}")

            yield _force_escape(key), _force_escape(value)


def attrs_string(attrs: Mapping[str, Attribute]) -> str:
    result = " ".join(k if v is True else f'{k}="{v}"' for k, v in _generate_attrs(attrs))

    if not result:
        return ""

    return " " + result
