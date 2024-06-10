import argparse
from dataclasses import dataclass

from htpy.utils import html_to_htpy


@dataclass
class ConvertArgs:
    shorthand: bool
    format: bool


def main():
    global_parser = argparse.ArgumentParser(prog="htpy")
    subparsers = global_parser.add_subparsers(title="commands", help="commands")

    convert_parser = subparsers.add_parser(
        "convert", help="convert html to python (htpy)"
    )
    convert_parser.add_argument(
        "-s",
        "--shorthand",
        help="Use shorthand syntax for class and id attributes",
        action="store_true",
    )
    convert_parser.add_argument(
        "-f",
        "--format",
        help="Format output code (requires black installed)",
        action="store_true",
    )

    def _convert_html(args: ConvertArgs):
        convert_html_cli(args.shorthand, args.format)

    convert_parser.set_defaults(func=_convert_html)

    args = global_parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()


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

        output = html_to_htpy(collected_text, shorthand_id_class, format)
        print("\n##############################################")
        print("### serialized and formatted python (htpy) ###")
        print("##############################################\n")
        print(output)
    except KeyboardInterrupt:
        print("\nInterrupted")
