"""CLI entry point for patching a .env file from a diff against another."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.comparator import compare
from envdiff.parser import parse_env_file
from envdiff.patcher import patch, write_patch


def build_patch_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(
        prog="envdiff patch",
        description="Patch BASE_ENV with keys from SOURCE_ENV based on diff.",
    )
    parser = parent.add_parser("patch", **kwargs) if parent else argparse.ArgumentParser(**kwargs)
    parser.add_argument("base", metavar="BASE_ENV", help="File to patch")
    parser.add_argument("source", metavar="SOURCE_ENV", help="File to pull updates from")
    parser.add_argument("-o", "--output", metavar="FILE", help="Write patched env to FILE (default: stdout summary)")
    parser.add_argument("--no-add", action="store_true", help="Do not add missing keys")
    parser.add_argument("--no-update", action="store_true", help="Do not update mismatched keys")
    parser.add_argument("--skip", metavar="KEY", nargs="+", help="Keys to skip during patching")
    parser.add_argument("--strict", action="store_true", help="Exit 1 if any changes were applied")
    return parser


def _run_patch(args: argparse.Namespace) -> int:
    base_path = Path(args.base)
    source_path = Path(args.source)

    for p in (base_path, source_path):
        if not p.exists():
            print(f"error: file not found: {p}", file=sys.stderr)
            return 2

    base_env = parse_env_file(base_path)
    source_env = parse_env_file(source_path)
    diff = compare(base_env, source_env)

    result = patch(
        base_env,
        diff,
        add_missing=not args.no_add,
        update_mismatched=not args.no_update,
        skip_keys=args.skip or [],
    )

    print(result.summary())

    if args.output:
        out = Path(args.output)
        write_patch(out, result.patched)
        print(f"patched env written to {out}")

    if args.strict and result.has_changes():
        return 1
    return 0


def main() -> None:
    parser = build_patch_parser()
    args = parser.parse_args()
    sys.exit(_run_patch(args))


if __name__ == "__main__":  # pragma: no cover
    main()
