"""CLI entry point for the lint subcommand."""
from __future__ import annotations
import argparse
import sys
from envdiff.linter import lint_file


def build_lint_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    kwargs = dict(
        prog="envdiff lint",
        description="Lint .env files for style and correctness issues.",
    )
    if parent is not None:
        parser = parent.add_parser("lint", **kwargs)
    else:
        parser = argparse.ArgumentParser(**kwargs)
    parser.add_argument("files", nargs="+", metavar="FILE", help=".env files to lint")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit 1 if any issues found (default: always exit 0)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="suppress output for files with no issues",
    )
    return parser


def _run_lint(args: argparse.Namespace) -> int:
    any_issues = False
    for path in args.files:
        result = lint_file(path)
        if result.ok and args.quiet:
            continue
        print(result.summary())
        if not result.ok:
            any_issues = True
    return 1 if (args.strict and any_issues) else 0


def main(argv: list[str] | None = None) -> None:
    parser = build_lint_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_lint(args))


if __name__ == "__main__":
    main()
