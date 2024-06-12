import sys
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

    is_multiline = "\n" in _data

    _data = _data.replace("\n", "")

    # escape unescaped dblquote: " -> \"
    _data = re.compile(r'(?<![\\])"').sub('\\"', _data)

    template_string_pattern = re.compile(r"\{\{\s*[\w\.]+\s*\}\}")

    has_jinja_pattern = re.search(template_string_pattern, _data)
    if has_jinja_pattern:
        # regex replaces these 3 cases:
        # {{ var.xx }} -> { var.xx }
        # { -> {{
        # } -> }}
        template_string_replace_pattern = re.compile(
            r"(\{\{\s*[\w\.]+\s*\}\}|(?<![\{]){(?![\{])|(?<![\}])}(?![\}]))"
        )

        def replacer(match: re.Match[str]):
            captured = match.group(1)

            if captured.startswith("{{"):
                return captured[1:-1]

            if captured == "{":
                return "{{"

            return "}}"

        _data = template_string_replace_pattern.sub(replacer, _data)
        if is_multiline:
            _data = '""' + _data + '""'

        _data = 'f"' + _data + '"'
    else:
        if is_multiline:
            _data = '""' + _data + '""'

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
    parser.add_argument(
        "input",
        type=argparse.FileType("r"),
        nargs="?",
        default=sys.stdin,
        help="input html from file or stdin",
    )

    args = parser.parse_args()

    try:
        if args.input == sys.stdin:
            input = args.input.read()
        elif args.input != sys.stdin:
            input = args.input.read()
        else:
            _printerr(
                "No input provided. Please supply an input file or stream.",
            )
            _printerr("Example usage: `cat index.html | html2htpy`")
            _printerr("`html2htpy -h` for help")
            sys.exit(1)
    except KeyboardInterrupt:
        _printerr(
            "\nInterrupted",
        )
        sys.exit(1)

    shorthand: bool = args.shorthand
    format: bool = args.format

    print(html2htpy(input, shorthand, format))


def _printerr(value: str):
    print(value, file=sys.stderr)


if __name__ == "__main__":
    main()
