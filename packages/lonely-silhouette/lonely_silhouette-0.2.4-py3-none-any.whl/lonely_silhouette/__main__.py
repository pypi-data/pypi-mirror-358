from argparse import ArgumentParser
from logging import DEBUG, basicConfig, getLogger
import sys
from typing import Sequence
from lonely_silhouette import lonely_silhouette, FontStyle

logger = getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "text",
        nargs="?",
        type=str,
        help="Text to become lonely silhouette (default: stdin)",
    )
    parser.add_argument(
        "--font-style",
        choices=FontStyle,
        default=FontStyle.ITALIC,
        type=FontStyle,
        help="silhouette style",
    )
    parser.add_argument("--verbose", action="store_true", help="show debug log")

    args = parser.parse_args(argv)

    if args.verbose:
        basicConfig(level=DEBUG)

    logger.debug(args)

    if args.text:
        print(lonely_silhouette(args.text, font_style=args.font_style))
    elif not sys.stdin.isatty():
        for line in sys.stdin:
            print(lonely_silhouette(line, font_style=args.font_style))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
