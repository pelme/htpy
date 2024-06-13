import argparse
import re
import shutil
import subprocess
import sys
from abc import ABC, abstractmethod
from html.parser import HTMLParser
from typing import Any, Literal

__all__ = ["html2htpy"]

_void_elements = [
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
]


class Tag:
    def __init__(
        self,
        type: str,
        attrs: list[tuple[str, str | None]],
        parent: Any | None = None,
    ):
        self.html_type = type
        self.python_type = type
        if "-" in self.python_type:
            self.python_type = self.python_type.replace("-", "_")

        self.attrs = attrs
        self.parent = parent
        self.children: list[Any | str] = []

    def serialize(self, shorthand_id_class: bool, use_h_prefix: bool) -> str:
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
                if _positional_attrs["id"] is None:
                    raise Exception("Id attribute cannot be none")

                arg0 += "#" + _positional_attrs["id"]

            if "class" in _positional_attrs:
                if _positional_attrs["class"] is None:
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
                    _children += c.serialize(shorthand_id_class, use_h_prefix)
                else:
                    _children += str(c)

                _children += ","

            _children = _children[:-1] + "]"

        if use_h_prefix:
            return f"h.{self.python_type}{_attrs}{_children}"

        return f"{self.python_type}{_attrs}{_children}"


class Formatter(ABC):
    @abstractmethod
    def format(self, s: str) -> str:
        raise NotImplementedError()


class BlackFormatter(Formatter):
    def format(self, s: str) -> str:
        result = subprocess.run(
            ["black", "-q", "-"],
            input=s.encode("utf8"),
            stdout=subprocess.PIPE,
        )
        return result.stdout.decode("utf8")


class RuffFormatter(Formatter):
    def format(self, s: str) -> str:
        result = subprocess.run(
            ["ruff", "format", "-"],
            input=s.encode("utf8"),
            stdout=subprocess.PIPE,
        )
        return result.stdout.decode("utf8")


class HTPYParser(HTMLParser):
    def __init__(self) -> None:
        self._collected: list[Tag | str] = []
        self._current: Tag | None = None
        super().__init__()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = Tag(tag, attrs, parent=self._current)

        if not self._current:
            self._collected.append(t)
        else:
            self._current.children.append(t)

        if tag not in _void_elements:
            self._current = t

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = Tag(tag, attrs, parent=self._current)

        if not self._current:
            self._collected.append(t)
        else:
            self._current.children.append(t)

    def handle_endtag(self, tag: str) -> None:
        if not self._current:
            raise Exception(f"Error parsing html: Closing tag {tag} when not inside any other tag")

        if not self._current.html_type == tag:
            raise Exception(
                f"Error parsing html: Closing tag {tag} does not match the "
                f"currently open tag ({self._current.html_type})"
            )

        self._current = self._current.parent

    def handle_data(self, data: str) -> None:
        if not data.isspace():
            stringified_data = _convert_data_to_string(data)

            if self._current:
                self._current.children.append(stringified_data)
            else:
                self._collected.append(stringified_data)

    def serialize_python(
        self,
        shorthand_id_class: bool = False,
        import_mode: Literal["yes", "h", "no"] = "yes",
        formatter: Formatter | None = None,
    ) -> str:
        o = ""

        use_h_prefix = False

        if import_mode == "yes":
            unique_tags: set[str] = set()

            def _tags_from_children(parent: Tag) -> None:
                for c in parent.children:
                    if isinstance(c, Tag):
                        unique_tags.add(c.python_type)
                        _tags_from_children(c)

            for t in self._collected:
                if isinstance(t, Tag):
                    unique_tags.add(t.python_type)
                    _tags_from_children(t)

            sorted_tags = list(unique_tags)
            sorted_tags.sort()

            o += f'from htpy import {", ".join(sorted_tags)}\n'

        elif import_mode == "h":
            o += "import htpy as h\n"
            use_h_prefix = True

        if len(self._collected) == 1:
            o += _serialize(self._collected[0], shorthand_id_class, use_h_prefix)

        else:
            o += "["
            for t in self._collected:
                o += _serialize(t, shorthand_id_class, use_h_prefix) + ","
            o = o[:-1] + "]"

        if formatter:
            return formatter.format(o)
        else:
            return o


def html2htpy(
    html: str,
    shorthand_id_class: bool = True,
    import_mode: Literal["yes", "h", "no"] = "yes",
    formatter: Formatter | None = None,
) -> str:
    parser = HTPYParser()
    parser.feed(html)

    return parser.serialize_python(shorthand_id_class, import_mode, formatter)


def _convert_data_to_string(data: str) -> str:
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

        def replacer(match: re.Match[str]) -> str:
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


def _serialize(el: Tag | str, shorthand_id_class: bool, use_h_prefix: bool) -> str:
    if isinstance(el, Tag):
        return el.serialize(shorthand_id_class, use_h_prefix)
    else:
        return str(el)


def _get_formatter(format: Literal["auto", "ruff", "black", "none"]) -> Formatter | None:
    if format == "ruff":
        if _is_command_available("ruff"):
            return RuffFormatter()
        else:
            _printerr(
                "Selected formatter (ruff) is not installed.",
            )
            _printerr("Please install it or select another formatter.")
            _printerr("`html2htpy -h` for help")
            sys.exit(1)

    if format == "black":
        if _is_command_available("black"):
            return BlackFormatter()
        else:
            _printerr(
                "Selected formatter (black) is not installed.",
            )
            _printerr("Please install it or select another formatter.")
            _printerr("`html2htpy -h` for help")
            sys.exit(1)

    elif format == "auto":
        if _is_command_available("black"):
            return BlackFormatter()
        if _is_command_available("ruff"):
            return RuffFormatter()

    return None


def _is_command_available(command: str) -> bool:
    return shutil.which(command) is not None


def main() -> None:
    parser = argparse.ArgumentParser(prog="html2htpy")

    parser.add_argument(
        "-f",
        "--format",
        choices=["auto", "ruff", "black", "none"],
        default="auto",
        help="Select one of the following formatting options: auto, ruff, black or none",
    )
    parser.add_argument(
        "-i",
        "--imports",
        choices=["yes", "h", "no"],
        help="Output mode for imports of found htpy elements",
        default="yes",
    )
    parser.add_argument(
        "--no-shorthand",
        help="Use explicit `id` and `class_` kwargs instead of the shorthand #id.class syntax",
        action="store_true",
    )
    parser.add_argument(
        "input",
        type=argparse.FileType("r"),
        nargs="?",
        default=sys.stdin,
        help="input HTML from file or stdin",
    )

    args = parser.parse_args()

    try:
        input = args.input.read()
    except KeyboardInterrupt:
        _printerr(
            "\nInterrupted",
        )
        sys.exit(1)

    shorthand = not args.no_shorthand
    imports: Literal["yes", "h", "no"] = args.imports

    formatter = _get_formatter(args.format)

    print(html2htpy(input, shorthand, imports, formatter))


def _printerr(value: str) -> None:
    print(value, file=sys.stderr)
