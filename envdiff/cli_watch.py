"""CLI entry point for `envdiff watch`."""
from __future__ import annotations

import argparse
import sys

from envdiff.watcher import watch, ChangeEvent
from envdiff.reporter import render
from envdiff.comparator import has_differences


def build_watch_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    kwargs = dict(description="Watch .env files for changes and print diffs.")
    if parent is not None:
        p = parent.add_parser("watch", **kwargs)
    else:
        p = argparse.ArgumentParser(prog="envdiff-watch", **kwargs)
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to watch")
    p.add_argument("--interval", type=float, default=1.0, metavar="SEC", help="Poll interval in seconds (default: 1.0)")
    p.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    p.add_argument("--max-cycles", type=int, default=None, metavar="N", help="Stop after N poll cycles (useful for testing)")
    return p


def _run_watch(args: argparse.Namespace) -> int:
    fmt = args.fmt

    def on_change(event: ChangeEvent) -> None:
        print(f"[envdiff] change detected: {event.path}")
        if has_differences(event.diff):
            print(render(event.diff, fmt=fmt))
        else:
            print("  (no key differences)")

    try:
        watch(
            paths=args.files,
            on_change=on_change,
            interval=args.interval,
            max_cycles=args.max_cycles,
        )
    except KeyboardInterrupt:
        print("\n[envdiff] watch stopped.")
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_watch_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_watch(args))


if __name__ == "__main__":
    main()
