"""CLI sub-command: envdiff export — write diff results to a file or stdout."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.comparator import compare
from envdiff.exporter import ExportFormat, export
from envdiff.parser import parse_env_file

_FORMATS: list[ExportFormat] = ["json", "csv", "markdown"]


def build_export_parser(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Attach the 'export' sub-command to an existing subparsers group."""
    p = subparsers.add_parser(
        "export",
        help="Export diff results to json, csv, or markdown.",
    )
    p.add_argument("first", help="Path to the first .env file.")
    p.add_argument("second", help="Path to the second .env file.")
    p.add_argument(
        "--format",
        dest="fmt",
        choices=_FORMATS,
        default="json",
        help="Output format (default: json).",
    )
    p.add_argument(
        "--output",
        "-o",
        dest="output",
        default=None,
        help="Write output to this file instead of stdout.",
    )
    p.set_defaults(func=_run_export)


def _run_export(args: argparse.Namespace) -> int:
    """Execute the export sub-command; returns an exit code."""
    try:
        first = parse_env_file(Path(args.first))
        second = parse_env_file(Path(args.second))
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    result = compare(first, second)
    output = export(result, args.fmt)

    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
        print(f"Exported to {args.output}")
    else:
        sys.stdout.write(output)

    return 0


def main(argv: list[str] | None = None) -> int:
    """Standalone entry-point for the export sub-command (for testing)."""
    parser = argparse.ArgumentParser(prog="envdiff-export")
    subs = parser.add_subparsers(dest="command")
    build_export_parser(subs)
    args = parser.parse_args(argv if argv is not None else sys.argv[1:])
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)
