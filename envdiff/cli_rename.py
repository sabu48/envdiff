"""CLI entry point for applying a rename map to a diff."""
import argparse
import sys
from envdiff.parser import parse_env_file
from envdiff.comparator import compare
from envdiff.reporter import render
from envdiff.renamer import load_rename_map, apply_rename


def build_rename_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-rename",
        description="Compare .env files and apply a key rename map before reporting.",
    )
    p.add_argument("first", help="First .env file")
    p.add_argument("second", help="Second .env file")
    p.add_argument(
        "--rename-map",
        metavar="FILE",
        required=True,
        help="File containing OLD_KEY=NEW_KEY mappings",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if differences exist",
    )
    return p


def _run_rename(args: argparse.Namespace) -> int:
    first = parse_env_file(args.first)
    second = parse_env_file(args.second)
    diff = compare(first, second)
    rename_map = load_rename_map(args.rename_map)
    diff = apply_rename(diff, rename_map)
    print(render(diff, fmt=args.fmt))
    if args.strict and diff.missing_in_second or diff.missing_in_first or diff.mismatched:
        return 1
    return 0


def main() -> None:
    parser = build_rename_parser()
    args = parser.parse_args()
    sys.exit(_run_rename(args))


if __name__ == "__main__":
    main()
