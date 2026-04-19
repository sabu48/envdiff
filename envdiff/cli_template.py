"""CLI entry-point: envdiff-template — generate a .env.template from env files."""
from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.templater import build_template, save_template


def build_template_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-template",
        description="Generate a .env.template from one or more .env files.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help="Input .env files")
    p.add_argument(
        "-o", "--output", default=None, metavar="OUT",
        help="Write template to this file (default: print to stdout)",
    )
    p.add_argument(
        "--placeholder", default="", metavar="TEXT",
        help="Value placeholder (default: empty string)",
    )
    p.add_argument(
        "--no-sort", action="store_true",
        help="Preserve key insertion order instead of sorting",
    )
    return p


def _run(args: argparse.Namespace) -> int:
    envs = []
    for path in args.files:
        try:
            envs.append(parse_env_file(path))
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2

    result = build_template(*envs, sort_keys=not args.no_sort)

    if args.output:
        save_template(result, args.output, placeholder=args.placeholder)
        print(f"Template written to {args.output}")
    else:
        print(result.render(placeholder=args.placeholder), end="")

    return 0


def main(argv=None) -> None:
    parser = build_template_parser()
    args = parser.parse_args(argv)
    sys.exit(_run(args))


if __name__ == "__main__":
    main()
