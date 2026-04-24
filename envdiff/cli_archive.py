"""CLI entry-point for the archive sub-command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from envdiff.archiver import load_archive, save_archive


def build_archive_parser(parent: Optional[argparse._SubParsersAction] = None) -> argparse.ArgumentParser:  # type: ignore[type-arg]
    description = "Archive .env files into a zip bundle or inspect an existing archive."
    if parent is not None:
        parser = parent.add_parser("archive", description=description, help=description)
    else:
        parser = argparse.ArgumentParser(prog="envdiff-archive", description=description)

    sub = parser.add_subparsers(dest="archive_cmd", required=True)

    # --- save sub-command ---
    save_p = sub.add_parser("save", help="Bundle .env files into a zip archive.")
    save_p.add_argument("files", nargs="+", metavar="FILE", help=".env files to archive")
    save_p.add_argument("-o", "--output", required=True, metavar="OUT", help="Destination zip file")
    save_p.add_argument(
        "--labels",
        nargs="+",
        metavar="LABEL",
        help="Optional labels (one per file); defaults to filenames",
    )

    # --- inspect sub-command ---
    inspect_p = sub.add_parser("inspect", help="Print metadata and key counts for an archive.")
    inspect_p.add_argument("archive", metavar="ARCHIVE", help="Zip archive to inspect")

    return parser


def _run_save(args: argparse.Namespace) -> int:
    files: List[Path] = [Path(f) for f in args.files]
    missing = [str(f) for f in files if not f.exists()]
    if missing:
        for m in missing:
            print(f"error: file not found: {m}", file=sys.stderr)
        return 2

    labels = args.labels or None
    if labels is not None and len(labels) != len(files):
        print(
            f"error: --labels count ({len(labels)}) must match file count ({len(files)})",
            file=sys.stderr,
        )
        return 2

    out = Path(args.output)
    save_archive(files, out, labels=labels)
    print(f"Archived {len(files)} file(s) → {out}")
    return 0


def _run_inspect(args: argparse.Namespace) -> int:
    src = Path(args.archive)
    if not src.exists():
        print(f"error: archive not found: {src}", file=sys.stderr)
        return 2

    result = load_archive(src)
    print(f"Archive : {src}")
    print(f"Created : {result.meta.created_at}")
    print(f"Envs    : {result.meta.file_count}")
    print()
    for label in result.env_names:
        env = result.get(label) or {}
        print(f"  [{label}]  {len(env)} key(s)")
    return 0


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_archive_parser()
    args = parser.parse_args(argv)
    if args.archive_cmd == "save":
        sys.exit(_run_save(args))
    else:
        sys.exit(_run_inspect(args))


if __name__ == "__main__":  # pragma: no cover
    main()
