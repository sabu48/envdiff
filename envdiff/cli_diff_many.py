"""CLI entry point for diffing multiple .env files against a baseline."""
import argparse
import sys

from envdiff.differ import diff_many
from envdiff.reporter import render
from envdiff.sorter import SortOrder


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-many",
        description="Diff multiple .env files against a baseline file.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files; first is the baseline.")
    p.add_argument(
        "--baseline",
        type=int,
        default=0,
        metavar="N",
        help="Index of the baseline file (default: 0).",
    )
    p.add_argument("--pattern", default=None, help="Filter keys by glob pattern.")
    p.add_argument(
        "--category",
        choices=["missing_in_second", "missing_in_first", "mismatched"],
        default=None,
        help="Show only keys in this category.",
    )
    p.add_argument(
        "--sort",
        choices=[o.value for o in SortOrder],
        default=SortOrder.KEY.value,
        help="Sort order for keys (default: key).",
    )
    p.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    p.add_argument(
        "--fail-on-diff",
        action="store_true",
        help="Exit with code 1 if any differences are found.",
    )
    return p


def _run(args: argparse.Namespace) -> int:
    sort_order = SortOrder(args.sort)
    try:
        results = diff_many(
            args.files,
            baseline=args.baseline,
            pattern=args.pattern,
            category=args.category,
            sort=sort_order,
        )
    except (ValueError, IndexError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    has_any_diff = False
    for path, result in zip(
        [f for i, f in enumerate(args.files) if i != args.baseline], results
    ):
        print(f"--- baseline vs {path} ---")
        print(render(result, fmt=args.fmt))
        if result.missing_in_second or result.missing_in_first or result.mismatched:
            has_any_diff = True

    if args.fail_on_diff and has_any_diff:
        return 1
    return 0


def main():
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(_run(args))


if __name__ == "__main__":
    main()
