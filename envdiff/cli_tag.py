"""CLI entry-point: envdiff-tag — display .env keys grouped by tag."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List

from envdiff.parser import parse_env_file
from envdiff.tagger import build_tag_map, tag
from envdiff.tag_reporter import render_tag


def build_tag_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-tag",
        description="Display .env keys grouped by tag definitions.",
    )
    p.add_argument("env_file", help="Path to the .env file")
    p.add_argument(
        "--tags",
        metavar="JSON",
        help='JSON object mapping tag names to lists of keys, e.g. \'{"db":["DB_URL"]}\'",
        default="{}",
    )
    p.add_argument(
        "--tags-file",
        metavar="FILE",
        help="Path to a JSON file with tag definitions (overrides --tags)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    return p


def _load_rules(args: argparse.Namespace) -> Dict[str, List[str]]:
    if args.tags_file:
        with open(args.tags_file) as fh:
            return json.load(fh)
    return json.loads(args.tags)


def _run_tag(args: argparse.Namespace) -> int:
    path = Path(args.env_file)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2

    env = parse_env_file(path)
    rules = _load_rules(args)
    tm = build_tag_map(rules)
    result = tag(env, tm)
    print(render_tag(result, fmt=args.format), end="")
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_tag_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_tag(args))


if __name__ == "__main__":  # pragma: no cover
    main()
