"""CLI entry-point for the audit-log sub-command."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from envdiff.auditor import load_audit_log, AuditLog
from envdiff.audit_reporter import render_audit


def build_audit_parser(parent: argparse._SubParsersAction | None = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    description = "Display or query the envdiff audit log."
    if parent is not None:
        parser = parent.add_parser("audit", help=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-audit", description=description)

    parser.add_argument("log_file", help="Path to the JSON audit log file")
    parser.add_argument(
        "--format", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--operation", metavar="OP",
        help="Filter entries by operation name (e.g. diff, lint, merge)",
    )
    parser.add_argument(
        "--since", metavar="TIMESTAMP", type=float,
        help="Only show entries at or after this POSIX timestamp",
    )
    return parser


def _run_audit(args: argparse.Namespace) -> int:
    path = Path(args.log_file)
    if not path.exists():
        print(f"error: audit log not found: {path}", file=sys.stderr)
        return 2

    try:
        log: AuditLog = load_audit_log(path)
    except Exception as exc:  # noqa: BLE001
        print(f"error: could not read audit log: {exc}", file=sys.stderr)
        return 2

    if args.since is not None:
        log = log.since(args.since)

    if args.operation:
        log = log.by_operation(args.operation)

    print(render_audit(log, fmt=args.format), end="")
    return 0


def main(argv: list[str] | None = None) -> None:
    parser = build_audit_parser()
    args = parser.parse_args(argv)
    sys.exit(_run_audit(args))


if __name__ == "__main__":  # pragma: no cover
    main()
