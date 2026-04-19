"""CLI entry point for the `envdiff profile` command."""
from __future__ import annotations
import argparse
import json
import sys
from envdiff.profiler import profile


def build_profile_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    desc = "Profile a .env file and report statistics."
    if parent is not None:
        parser = parent.add_parser("profile", help=desc)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-profile", description=desc)
    parser.add_argument("file", help="Path to .env file")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--max-value-len", type=int, default=256, dest="max_value_len")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if issues found")
    return parser


def _run_profile(args: argparse.Namespace) -> int:
    try:
        result = profile(args.file, max_value_len=args.max_value_len)
    except OSError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps({
            "path": result.path,
            "total_keys": result.total_keys,
            "empty_keys": result.empty_keys,
            "duplicate_keys": result.duplicate_keys,
            "long_keys": result.long_keys,
        }, indent=2))
    else:
        print(f"File   : {result.path}")
        print(f"Summary: {result.summary()}")
        if result.empty_keys:
            print("Empty  : " + ", ".join(result.empty_keys))
        if result.duplicate_keys:
            print("Dupes  : " + ", ".join(result.duplicate_keys))
        if result.long_keys:
            print("Long   : " + ", ".join(result.long_keys))
        if not result.has_issues():
            print("No issues found.")

    return 1 if (args.strict and result.has_issues()) else 0


def main(argv: list[str] | None = None) -> None:
    parser = build_profile_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_profile(args))


if __name__ == "__main__":
    main()
