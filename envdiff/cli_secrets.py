"""CLI entry point for the secrets scanner subcommand.

Usage:
    envdiff-scan  (via cli_scan.py)
    python -m envdiff.cli_secrets scan .env.production --strict
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.secrets_scanner import scan, ScanResult


def build_secrets_parser(subparsers=None) -> argparse.ArgumentParser:
    """Build (or attach) the argument parser for the secrets-scan command."""
    description = "Scan one or more .env files for potentially exposed secrets."

    if subparsers is not None:
        parser = subparsers.add_parser(
            "secrets",
            help="Scan .env files for secrets",
            description=description,
        )
    else:
        parser = argparse.ArgumentParser(
            prog="envdiff-secrets",
            description=description,
        )

    parser.add_argument(
        "files",
        nargs="+",
        metavar="FILE",
        help="One or more .env files to scan.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any secrets are detected.",
    )
    parser.add_argument(
        "--show-values",
        action="store_true",
        dest="show_values",
        help="Include a redacted preview of the offending value in output.",
    )
    return parser


def _format_text(results: dict[str, ScanResult], show_values: bool) -> str:
    """Render scan results as human-readable text."""
    lines: list[str] = []
    for filename, result in results.items():
        lines.append(f"File: {filename}")
        lines.append(f"  Scanned : {result.scanned}")
        if result.clean():
            lines.append("  Status  : clean — no secrets detected")
        else:
            lines.append(f"  Status  : {len(result.hits)} potential secret(s) found")
            for hit in result.hits:
                entry = f"    [{hit.rule}] {hit.key}"
                if show_values and hit.preview:
                    entry += f"  =>  {hit.preview}"
                lines.append(entry)
        lines.append("")
    return "\n".join(lines).rstrip()


def _format_json(results: dict[str, ScanResult], show_values: bool) -> str:
    """Render scan results as JSON."""
    output: dict = {}
    for filename, result in results.items():
        hits_data = []
        for hit in result.hits:
            record: dict = {"key": hit.key, "rule": hit.rule}
            if show_values:
                record["preview"] = hit.preview
            hits_data.append(record)
        output[filename] = {
            "scanned": result.scanned,
            "clean": result.clean(),
            "hits": hits_data,
        }
    return json.dumps(output, indent=2)


def _run_secrets(args: argparse.Namespace) -> int:
    """Execute the secrets scan and return an exit code."""
    results: dict[str, ScanResult] = {}
    missing: list[str] = []

    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            print(f"error: file not found: {filepath}", file=sys.stderr)
            missing.append(filepath)
            continue
        env = parse_env_file(path)
        results[filepath] = scan(env)

    if missing:
        return 2

    if args.fmt == "json":
        print(_format_json(results, args.show_values))
    else:
        print(_format_text(results, args.show_values))

    if args.strict and any(not r.clean() for r in results.values()):
        return 1
    return 0


def main(argv: list[str] | None = None) -> None:  # pragma: no cover
    """Standalone entry point for the secrets scanner CLI."""
    parser = build_secrets_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_secrets(args))


if __name__ == "__main__":  # pragma: no cover
    main()
