"""CLI entry-point for snapshot commands: take, diff."""

from __future__ import annotations

import argparse
import sys

from envdiff.snapshot_reporter import render_snapshot_diff
from envdiff.snapshotter import diff_snapshots, load_snapshot, save_snapshot, take_snapshot


def build_snapshot_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff-snapshot",
        description="Snapshot and compare .env files over time.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    take_p = sub.add_parser("take", help="Capture a snapshot of one or more .env files.")
    take_p.add_argument("files", nargs="+", help=".env files to snapshot")
    take_p.add_argument("-o", "--output", required=True, help="Destination JSON file")
    take_p.add_argument("-l", "--labels", nargs="+", help="Optional labels for each file")

    diff_p = sub.add_parser("diff", help="Compare two snapshot files.")
    diff_p.add_argument("old", help="Older snapshot JSON")
    diff_p.add_argument("new", help="Newer snapshot JSON")
    diff_p.add_argument("-f", "--format", choices=["text", "json"], default="text")
    diff_p.add_argument(
        "--fail-on-changes",
        action="store_true",
        help="Exit 1 if any changes are detected",
    )

    return parser


def _run_take(args: argparse.Namespace) -> int:
    snap = take_snapshot(args.files, labels=args.labels)
    save_snapshot(snap, args.output)
    print(f"Snapshot saved to {args.output}")
    return 0


def _run_diff(args: argparse.Namespace) -> int:
    old = load_snapshot(args.old)
    new = load_snapshot(args.new)
    diff = diff_snapshots(old, new)
    print(render_snapshot_diff(diff, fmt=args.format))
    if args.fail_on_changes and diff:
        return 1
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_snapshot_parser()
    args = parser.parse_args(argv)
    if args.command == "take":
        code = _run_take(args)
    else:
        code = _run_diff(args)
    sys.exit(code)


if __name__ == "__main__":  # pragma: no cover
    main()
