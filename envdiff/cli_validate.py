"""CLI sub-command: validate a single .env file against a schema file."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.validator import KeySchema, validate


def build_validate_parser(subparsers=None) -> argparse.ArgumentParser:
    desc = "Validate a .env file against a JSON schema of required keys and patterns."
    if subparsers is not None:
        parser = subparsers.add_parser("validate", help=desc)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-validate", description=desc)

    parser.add_argument("env_file", help="Path to the .env file to validate")
    parser.add_argument(
        "schema_file",
        help=(
            "Path to a JSON schema file with optional keys "
            "'required' (list) and 'patterns' (object)"
        ),
    )
    parser.add_argument(
        "--exit-one",
        action="store_true",
        help="Exit with code 1 when validation fails",
    )
    return parser


def _run_validate(args: argparse.Namespace) -> int:
    env = parse_env_file(Path(args.env_file))

    raw = json.loads(Path(args.schema_file).read_text())
    schema = KeySchema(
        required=set(raw.get("required", [])),
        patterns=raw.get("patterns", {}),
    )

    result = validate(env, schema)
    print(result.summary())

    if not result.is_valid and args.exit_one:
        return 1
    return 0


def main(argv=None) -> None:
    parser = build_validate_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_validate(args))


if __name__ == "__main__":
    main()
