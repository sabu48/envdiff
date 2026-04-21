"""CLI entry-point: envdiff-group — show diff keys grouped by prefix."""
from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.comparator import compare
from envdiff.grouper import group_diff
from envdiff.group_reporter import render_group


def build_group_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-group",
        description="Compare two .env files and display differences grouped by key prefix.",
    )
    p.add_argument("first", help="First .env file")
    p.add_argument("second", help="Second .env file")
    p.add_argument(
        "--separator",
        default="_",
        metavar="SEP",
        help="Prefix separator character (default: '_')",
    )
    p.add_argument(
        "--min-group-size",
        type=int,
        default=1,
        metavar="N",
        help="Minimum keys for a prefix to form its own group (default: 1)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 when differences are found",
    )
    return p


def _run(args: argparse.Namespace) -> int:
    try:
        env_a = parse_env_file(args.first)
        env_b = parse_env_file(args.second)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    result = compare(env_a, env_b)
    report = group_diff(result, separator=args.separator, min_group_size=args.min_group_size)
    print(render_group(report, fmt=args.fmt), end="")

    if args.strict and (result.missing_in_first or result.missing_in_second or result.mismatched):
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_group_parser()
    args = parser.parse_args()
    sys.exit(_run(args))


if __name__ == "__main__":  # pragma: no cover
    main()
