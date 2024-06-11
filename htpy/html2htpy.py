import re
import argparse
from dataclasses import dataclass
from typing import Self
from html.parser import HTMLParser

__all__ = ["html2htpy"]


class Tag:
    def __init__(
        self,
        type: str,
        attrs: list[tuple[str, str | None]],
        parent: Self | None = None,
    ):
        self.type = type
        self.attrs = attrs
        self.parent = parent
        self.children: list[Self | str] = []

    def serialize(self, shorthand_id_class: bool = False):
        _type = self.type
        if "-" in _type:
            _type = _type.replace("-", "_")

        _positional_attrs: dict[str, str | None] = {}
        _attrs = ""
        _kwattrs: list[tuple[str, str | None]] = []

        for a in self.attrs:
            key = a[0]
            if key == "class":
                if shorthand_id_class:
                    _positional_attrs[key] = a[1]
                else:
                    _kwattrs.append(a)

            elif key == "id":
                if shorthand_id_class:
                    _positional_attrs[key] = a[1]
                else:
                    _kwattrs.append(a)
            else:
                _kwattrs.append(a)

        if _positional_attrs or _kwattrs:
            _attrs += "("

        if _positional_attrs:
            arg0 = ""
            if "id" in _positional_attrs:
                if _positional_attrs["id"] == None:
                    raise Exception("Id attribute cannot be none")

                arg0 += "#" + _positional_attrs["id"]

            if "class" in _positional_attrs:
                if _positional_attrs["class"] == None:
                    raise Exception("Class attribute cannot be none")

                classes = ".".join(_positional_attrs["class"].split(" "))
                arg0 += "." + classes

            _attrs += '"' + arg0 + '",'

        if _kwattrs:
            for a in _kwattrs:
                key = a[0]
                if "-" in key:
                    key = key.replace("-", "_")

                if key == "class":
                    key = "class_"
                elif key == "for":
                    key = "for_"

                val = a[1]
                if not val:
                    _attrs += f"{key}=True,"

                else:
                    _attrs += f'{key}="{val}",'

        if _positional_attrs or _kwattrs:
            _attrs = _attrs[:-1] + ")"

        _children: str = ""
        if self.children:
            _children += "["
            for c in self.children:
                if isinstance(c, Tag):
                    _children += c.serialize(shorthand_id_class=shorthand_id_class)
                else:
                    _children += str(c)

                _children += ","

            _children = _children[:-1] + "]"

        return f"{_type}{_attrs}{_children}"


class HTPYParser(HTMLParser):
    def __init__(self):
        self._collected: list[Tag | str] = []
        self._current: Tag | None = None
        super().__init__()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]):
        t = Tag(tag, attrs, parent=self._current)

        if not self._current:
            self._collected.append(t)
        else:
            self._current.children.append(t)

        self._current = t

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]):
        t = Tag(tag, attrs, parent=self._current)

        if not self._current:
            self._collected.append(t)
        else:
            self._current.children.append(t)

    def handle_endtag(self, tag: str):
        if not self._current:
            raise Exception(
                f"Error parsing html: Closing tag {tag} when not inside any other tag"
            )

        if not self._current.type == tag:
            raise Exception(
                f"Error parsing html: Closing tag {tag} does not match the currently open tag ({self._current.type})"
            )

        self._current = self._current.parent

    def handle_data(self, data: str):
        if not data.isspace():
            stringified_data = _convert_data_to_string(data)

            if self._current:
                self._current.children.append(stringified_data)
            else:
                self._collected.append(stringified_data)

    def serialize_python(self, shorthand_id_class: bool = False, format: bool = False):
        o = ""

        if len(self._collected) == 1:
            o += _serialize(self._collected[0], shorthand_id_class)

        else:
            o += "["
            for t in self._collected:
                o += _serialize(t, shorthand_id_class) + ","
            o = o[:-1] + "]"

        if format:
            try:
                import black
            except:
                raise Exception(
                    "Cannot import formatter. Please ensure black is installed."
                )

            return black.format_str(
                o, mode=black.FileMode(line_length=80, magic_trailing_comma=False)
            )
        else:
            return o


def html2htpy(html: str, shorthand_id_class: bool = False, format: bool = False):
    parser = HTPYParser()
    parser.feed(html)

    return parser.serialize_python(shorthand_id_class, format)


def _convert_data_to_string(data: str):
    _data = str(data)
    escaped_text = _data.replace('"', '\\"')

    pattern = re.compile(r"\{\{\s*(\w+)\s*\}\}")

    has_jinja_pattern = re.search(pattern, _data)
    if has_jinja_pattern:

        def replacer(match: re.Match[str]):
            var_name = match.group(1)
            return f"{{{var_name}}}"

        _data = pattern.sub(replacer, escaped_text)
        _data = 'f"' + _data + '"'
    else:
        _data = '"' + _data + '"'

    return _data


def _serialize(el: Tag | str, shorthand_id_class: bool):
    if isinstance(el, Tag):
        return el.serialize(shorthand_id_class=shorthand_id_class)
    else:
        return str(el)


@dataclass
class ConvertArgs:
    shorthand: bool
    format: bool


def main():
    parser = argparse.ArgumentParser(prog="html2htpy")

    parser.add_argument(
        "-s",
        "--shorthand",
        help="Use shorthand syntax for class and id attributes",
        action="store_true",
    )
    parser.add_argument(
        "-f",
        "--format",
        help="Format output code (requires black installed)",
        action="store_true",
    )

    def _convert_html(args: ConvertArgs):
        convert_html_cli(args.shorthand, args.format)

    parser.set_defaults(func=_convert_html)

    args = parser.parse_args()

    args.func(args)


def convert_html_cli(shorthand_id_class: bool, format: bool):
    import time

    print("")
    print(f"HTML to HTPY converter")
    print(f"selected options: ")
    print(f"              format: {format}")
    print(f"  shorthand id class: {shorthand_id_class}")
    print("\n>>>>>>>>>>>>>>>>>>")
    print(">>> paste html >>>")
    print(">>>>>>>>>>>>>>>>>>\n")

    collected_text = ""
    input_starttime = None

    try:
        while True:
            user_input = input()
            if not input_starttime:
                input_starttime = time.time()

            collected_text += user_input

            if input_starttime + 0.1 < time.time():
                break

        output = html2htpy(collected_text, shorthand_id_class, format)
        print("\n##############################################")
        print("### serialized and formatted python (htpy) ###")
        print("##############################################\n")
        print(output)
    except KeyboardInterrupt:
        print("\nInterrupted")


if __name__ == "__main__":
    main()
