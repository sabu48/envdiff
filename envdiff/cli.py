"""Command-line interface for envdiff."""
import sys
import argparse
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.comparator import compare
from envdiff.reporter import render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments and flag missing or mismatched keys.",
    )
    parser.add_argument("file1", type=Path, help="First .env file")
    parser.add_argument("file2", type=Path, help="Second .env file")
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 if differences are found",
    )
    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    for path in (args.file1, args.file2):
        if not path.exists():
            print(f"envdiff: error: file not found: {path}", file=sys.stderr)
            return 2

    env1 = parse_env_file(args.file1)
    env2 = parse_env_file(args.file2)

    result = compare(
        env1, env2,
        name1=str(args.file1),
        name2=str(args.file2),
    )

    print(render(result, fmt=args.fmt))

    if args.exit_code and result.has_differences():
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
