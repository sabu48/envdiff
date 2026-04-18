"""CLI entry point for drift detection."""
from __future__ import annotations

import argparse
import json
import sys

from envdiff.drift import detect_drift


def build_drift_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:
    kwargs = dict(description="Detect drift between a baseline snapshot and a live .env file.")
    if parent is not None:
        parser = parent.add_parser("drift", **kwargs)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-drift", **kwargs)
    parser.add_argument("baseline", help="Path to saved baseline JSON file")
    parser.add_argument("env", help="Path to live .env file")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text", help="Output format"
    )
    parser.add_argument(
        "--strict", action="store_true", help="Exit 1 if any drift is detected"
    )
    return parser


def _run_drift(args: argparse.Namespace) -> int:
    try:
        report = detect_drift(args.baseline, args.env)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        out = {
            "baseline": report.baseline_path,
            "env": report.env_path,
            "has_drift": report.has_drift,
            "new_keys": report.new_keys,
            "removed_keys": report.removed_keys,
            "changed_keys": report.changed_keys,
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"Baseline : {report.baseline_path}")
        print(f"Env file : {report.env_path}")
        print(report.summary())
        if report.new_keys:
            print("  New     : " + ", ".join(report.new_keys))
        if report.removed_keys:
            print("  Removed : " + ", ".join(report.removed_keys))
        if report.changed_keys:
            print("  Changed : " + ", ".join(report.changed_keys))

    if args.strict and report.has_drift:
        return 1
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_drift_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_drift(args))


if __name__ == "__main__":
    main()
