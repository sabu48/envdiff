"""CLI entry point for the secrets scanner sub-command."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.secrets_scanner import scan


def build_scan_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    description = "Scan .env file(s) for potentially exposed secrets."
    if parent is not None:
        parser = parent.add_parser("scan", help=description, description=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-scan", description=description)

    parser.add_argument("files", nargs="+", metavar="FILE", help=".env file(s) to scan")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any secrets are found",
    )
    return parser


def _run_scan(args: argparse.Namespace) -> int:
    all_clean = True
    output: list = []

    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            print(f"Error: file not found: {filepath}", file=sys.stderr)
            return 2

        env = parse_env_file(path)
        result = scan(env)

        if not result.clean:
            all_clean = False

        if args.format == "json":
            output.append({
                "file": filepath,
                "scanned": result.scanned,
                "clean": result.clean,
                "hits": [
                    {"key": h.key, "reason": h.reason, "value_preview": h.value_preview}
                    for h in result.hits
                ],
            })
        else:
            print(f"=== {filepath} ===")
            print(result.summary())
            print()

    if args.format == "json":
        print(json.dumps(output, indent=2))

    if args.strict and not all_clean:
        return 1
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_scan_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_scan(args))


if __name__ == "__main__":  # pragma: no cover
    main()
