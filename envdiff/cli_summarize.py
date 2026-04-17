"""CLI entry point for summarizing diffs across multiple .env files."""
import argparse
import json
import sys
from envdiff.parser import parse_env_file
from envdiff.summarizer import summarize


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-summarize",
        description="Summarize differences across multiple .env files.",
    )
    p.add_argument("files", nargs="+", metavar="FILE", help=".env files to summarize")
    p.add_argument(
        "--names",
        nargs="+",
        metavar="NAME",
        help="Labels for each file (defaults to filenames)",
    )
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
    )
    p.add_argument(
        "--fail-on-issues",
        action="store_true",
        help="Exit with code 1 if any issues are found",
    )
    return p


def _run(args: argparse.Namespace) -> int:
    names = args.names if args.names else args.files
    if len(names) != len(args.files):
        print("error: --names count must match file count", file=sys.stderr)
        return 2

    env_maps = {}
    for name, path in zip(names, args.files):
        try:
            env_maps[name] = parse_env_file(path)
        except FileNotFoundError:
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2

    summary = summarize(env_maps)

    if args.fmt == "json":
        out = {
            "envs": summary.env_names,
            "total_keys": summary.total_keys,
            "common_keys": summary.common_keys,
            "missing": {k: v for k, v in summary.all_missing.items()},
            "mismatched": summary.all_mismatched,
        }
        print(json.dumps(out, indent=2))
    else:
        print(f"Environments : {', '.join(summary.env_names)}")
        print(f"Total keys   : {summary.total_keys}")
        print(f"Common keys  : {len(summary.common_keys)}")
        if summary.all_missing:
            print("\nMissing keys:")
            for key, envs in sorted(summary.all_missing.items()):
                print(f"  {key}: missing in {', '.join(envs)}")
        if summary.all_mismatched:
            print("\nMismatched keys:")
            for key in summary.all_mismatched:
                print(f"  {key}")
        if not summary.has_issues():
            print("No issues found.")

    return 1 if (args.fail_on_issues and summary.has_issues()) else 0


def main():
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(_run(args))


if __name__ == "__main__":
    main()
