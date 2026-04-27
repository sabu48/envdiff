"""CLI entry-point: envdiff-health — run health checks on one or more .env files."""
from __future__ import annotations

import argparse
import sys
from typing import List

from envdiff.health import check
from envdiff.parser import parse_env_file


def build_health_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-health",
        description="Run health checks on .env files and report issues.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to check")
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any file is unhealthy (score < 80)",
    )
    p.add_argument(
        "--min-score",
        type=int,
        default=80,
        metavar="N",
        help="Minimum acceptable health score (default: 80)",
    )
    return p


def _run_health(files: List[str], min_score: int) -> List[bool]:
    """Check each file and print its report. Returns list of healthy flags."""
    results = []
    for path in files:
        try:
            env = parse_env_file(path)
        except FileNotFoundError:
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            results.append(False)
            continue

        report = check(path, env)
        healthy = report.score >= min_score
        results.append(healthy)

        header = f"=== {path} ==="
        print(header)
        print(report.summary())
        print()

    return results


def main(argv: List[str] | None = None) -> None:
    parser = build_health_parser()
    args = parser.parse_args(argv)

    healthy_flags = _run_health(args.files, args.min_score)

    if args.strict and not all(healthy_flags):
        sys.exit(1)


if __name__ == "__main__":  # pragma: no cover
    main()
