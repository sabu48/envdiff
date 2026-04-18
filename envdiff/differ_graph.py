"""Build a dependency/relationship graph between env files based on shared keys."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Set


@dataclass
class EnvNode:
    name: str
    keys: Set[str]


@dataclass
class EnvEdge:
    source: str
    target: str
    shared_keys: Set[str]
    only_in_source: Set[str]
    only_in_target: Set[str]

    @property
    def overlap_ratio(self) -> float:
        total = len(self.shared_keys | self.only_in_source | self.only_in_target)
        return len(self.shared_keys) / total if total else 1.0


@dataclass
class EnvGraph:
    nodes: Dict[str, EnvNode] = field(default_factory=dict)
    edges: List[EnvEdge] = field(default_factory=list)

    def get_edge(self, source: str, target: str) -> EnvEdge | None:
        for e in self.edges:
            if e.source == source and e.target == target:
                return e
        return None

    def most_similar(self) -> EnvEdge | None:
        return max(self.edges, key=lambda e: e.overlap_ratio, default=None)

    def least_similar(self) -> EnvEdge | None:
        return min(self.edges, key=lambda e: e.overlap_ratio, default=None)


def build_graph(envs: Dict[str, Dict[str, str | None]]) -> EnvGraph:
    """Build a graph from a mapping of env-name -> parsed env dict."""
    graph = EnvGraph()
    names = list(envs.keys())

    for name, env in envs.items():
        graph.nodes[name] = EnvNode(name=name, keys=set(env.keys()))

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            keys_a = graph.nodes[a].keys
            keys_b = graph.nodes[b].keys
            shared = keys_a & keys_b
            edge = EnvEdge(
                source=a,
                target=b,
                shared_keys=shared,
                only_in_source=keys_a - keys_b,
                only_in_target=keys_b - keys_a,
            )
            graph.edges.append(edge)

    return graph
