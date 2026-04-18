"""Format EnvGraph results as text or JSON for use in reports."""
from __future__ import annotations
import json
from typing import List
from envdiff.differ_graph import EnvGraph, EnvEdge


def _edge_to_dict(edge: EnvEdge) -> dict:
    return {
        "source": edge.source,
        "target": edge.target,
        "shared": sorted(edge.shared_keys),
        "only_in_source": sorted(edge.only_in_source),
        "only_in_target": sorted(edge.only_in_target),
        "overlap_ratio": round(edge.overlap_ratio, 4),
    }


def format_graph_json(graph: EnvGraph) -> str:
    data = {
        "nodes": [
            {"name": n.name, "key_count": len(n.keys)}
            for n in graph.nodes.values()
        ],
        "edges": [_edge_to_dict(e) for e in graph.edges],
    }
    return json.dumps(data, indent=2)


def format_graph_text(graph: EnvGraph) -> str:
    lines: List[str] = []
    lines.append(f"Nodes ({len(graph.nodes)}):")
    for node in graph.nodes.values():
        lines.append(f"  {node.name}: {len(node.keys)} keys")

    lines.append(f"\nEdges ({len(graph.edges)}):")
    for edge in sorted(graph.edges, key=lambda e: -e.overlap_ratio):
        pct = f"{edge.overlap_ratio:.0%}"
        lines.append(f"  {edge.source} <-> {edge.target}  [{pct} overlap]")
        if edge.shared_keys:
            lines.append(f"    shared: {', '.join(sorted(edge.shared_keys))}")
        if edge.only_in_source:
            lines.append(f"    only in {edge.source}: {', '.join(sorted(edge.only_in_source))}")
        if edge.only_in_target:
            lines.append(f"    only in {edge.target}: {', '.join(sorted(edge.only_in_target))}")

    best = graph.most_similar()
    if best:
        lines.append(f"\nMost similar : {best.source} <-> {best.target} ({best.overlap_ratio:.0%})")
    worst = graph.least_similar()
    if worst and worst is not best:
        lines.append(f"Least similar: {worst.source} <-> {worst.target} ({worst.overlap_ratio:.0%})")

    return "\n".join(lines)


def render_graph(graph: EnvGraph, fmt: str = "text") -> str:
    if fmt == "json":
        return format_graph_json(graph)
    return format_graph_text(graph)
