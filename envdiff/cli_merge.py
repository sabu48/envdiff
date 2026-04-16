"""CLI entry point for merging multiple .env files."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.merger import merge


def build_merge_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    kwargs = dict(
        description="Merge multiple .env files into one, reporting conflicts."
    )
    if parent is not None:
        parser = parent.add_parser("merge", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-merge", **kwargs)

    parser.add_argument("files", nargs="+", metavar="FILE", help=".env files to merge")
    parser.add_argument(
        "--strategy",
        choices=["first", "last"],
        default="last",
        help="Conflict resolution strategy (default: last)",
    )
    parser.add_argument(
        "--output", "-o", metavar="FILE", help="Write merged result to file"
    )
    parser.add_argument(
        "--format", choices=["env", "json"], default="env", dest="fmt"
    )
    parser.add_argument(
        "--fail-on-conflicts", action="store_true", help="Exit 1 if conflicts found"
    )
    return parser


def _run_merge(args: argparse.Namespace) -> int:
    envs = {}
    for path in args.files:
        p = Path(path)
        if not p.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 2
        envs[path] = parse_env_file(p)

    result = merge(envs, strategy=args.strategy)

    if result.has_conflicts():
        print(result.conflict_summary(), file=sys.stderr)

    if args.fmt == "json":
        output = json.dumps(result.merged, indent=2)
    else:
        output = "\n".join(
            f"{k}={v}" for k, v in sorted(result.merged.items()) if v is not None
        )

    if args.output:
        Path(args.output).write_text(output + "\n")
    else:
        print(output)

    return 1 if (args.fail_on_conflicts and result.has_conflicts()) else 0


def main() -> None:
    parser = build_merge_parser()
    args = parser.parse_args()
    sys.exit(_run_merge(args))


if __name__ == "__main__":
    main()
