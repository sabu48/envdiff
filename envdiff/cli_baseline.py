"""CLI entry-point for baseline save/compare operations."""
from __future__ import annotations

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.baseline import save_baseline, compare_to_baseline
from envdiff.reporter import render


def build_baseline_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-baseline",
        description="Save or compare an .env file against a baseline snapshot.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    save_p = sub.add_parser("save", help="Save current .env as baseline.")
    save_p.add_argument("env_file", help="Path to .env file")
    save_p.add_argument("baseline", help="Path to write baseline JSON")

    cmp_p = sub.add_parser("compare", help="Compare .env against saved baseline.")
    cmp_p.add_argument("env_file", help="Path to .env file")
    cmp_p.add_argument("baseline", help="Path to baseline JSON")
    cmp_p.add_argument(
        "--format", choices=["text", "json"], default="text", dest="fmt"
    )
    cmp_p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 when differences are found.",
    )

    return p


def _run_baseline(args: argparse.Namespace) -> int:
    if args.command == "save":
        env = parse_env_file(args.env_file)
        save_baseline(env, args.baseline)
        print(f"Baseline saved to {args.baseline}")
        return 0

    # compare
    current = parse_env_file(args.env_file)
    diff = compare_to_baseline(current, args.baseline)
    print(render(diff, fmt=args.fmt))
    if args.strict and (diff.missing_in_first or diff.missing_in_second or diff.mismatched):
        return 1
    return 0


def main() -> None:  # pragma: no cover
    parser = build_baseline_parser()
    args = parser.parse_args()
    sys.exit(_run_baseline(args))


if __name__ == "__main__":  # pragma: no cover
    main()
