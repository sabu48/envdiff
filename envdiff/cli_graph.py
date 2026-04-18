"""CLI entry point for the env graph command."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from envdiff.parser import parse_env_file
from envdiff.differ_graph import build_graph


def build_graph_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="envdiff-graph",
        description="Show relationship graph between .env files.",
    )
    p.add_argument("files", nargs="+", help=".env files to analyse")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--min-overlap", type=float, default=0.0,
                   help="Only show edges with overlap ratio >= value (0-1)")
    return p


def _run(args: argparse.Namespace) -> int:
    envs = {}
    for path in args.files:
        p = Path(path)
        if not p.exists():
            print(f"error: file not found: {path}", file=sys.stderr)
            return 2
        envs[p.name] = parse_env_file(p)

    graph = build_graph(envs)
    edges = [e for e in graph.edges if e.overlap_ratio >= args.min_overlap]

    if args.format == "json":
        data = [
            {
                "source": e.source,
                "target": e.target,
                "shared": sorted(e.shared_keys),
                "only_in_source": sorted(e.only_in_source),
                "only_in_target": sorted(e.only_in_target),
                "overlap_ratio": round(e.overlap_ratio, 4),
            }
            for e in edges
        ]
        print(json.dumps(data, indent=2))
    else:
        if not edges:
            print("No edges to display.")
        for e in edges:
            pct = f"{e.overlap_ratio:.0%}"
            print(f"{e.source} <-> {e.target}  overlap={pct}")
            if e.shared_keys:
                print(f"  shared       : {', '.join(sorted(e.shared_keys))}")
            if e.only_in_source:
                print(f"  only in {e.source}: {', '.join(sorted(e.only_in_source))}")
            if e.only_in_target:
                print(f"  only in {e.target}: {', '.join(sorted(e.only_in_target))}")
    return 0


def main() -> None:
    parser = build_graph_parser()
    args = parser.parse_args()
    sys.exit(_run(args))


if __name__ == "__main__":
    main()
