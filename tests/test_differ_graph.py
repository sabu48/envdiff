import pytest
from envdiff.differ_graph import build_graph, EnvGraph, EnvEdge


@pytest.fixture
def envs():
    return {
        "dev": {"DB_HOST": "localhost", "DB_PORT": "5432", "DEBUG": "true"},
        "staging": {"DB_HOST": "staging-db", "DB_PORT": "5432", "LOG_LEVEL": "info"},
        "prod": {"DB_HOST": "prod-db", "LOG_LEVEL": "warn"},
    }


@pytest.fixture
def graph(envs):
    return build_graph(envs)


def test_nodes_created(graph):
    assert set(graph.nodes.keys()) == {"dev", "staging", "prod"}


def test_node_keys(graph):
    assert graph.nodes["dev"].keys == {"DB_HOST", "DB_PORT", "DEBUG"}


def test_edges_count(graph):
    # 3 envs -> 3 pairs
    assert len(graph.edges) == 3


def test_shared_keys_dev_staging(graph):
    edge = graph.get_edge("dev", "staging")
    assert edge is not None
    assert edge.shared_keys == {"DB_HOST", "DB_PORT"}


def test_only_in_source(graph):
    edge = graph.get_edge("dev", "staging")
    assert "DEBUG" in edge.only_in_source


def test_only_in_target(graph):
    edge = graph.get_edge("dev", "staging")
    assert "LOG_LEVEL" in edge.only_in_target


def test_overlap_ratio_full(graph):
    envs = {"a": {"X": "1", "Y": "2"}, "b": {"X": "1", "Y": "2"}}
    g = build_graph(envs)
    edge = g.get_edge("a", "b")
    assert edge.overlap_ratio == 1.0


def test_overlap_ratio_partial(graph):
    edge = graph.get_edge("dev", "staging")
    assert 0 < edge.overlap_ratio < 1.0


def test_most_similar(graph):
    best = graph.most_similar()
    assert best is not None
    assert isinstance(best, EnvEdge)


def test_least_similar(graph):
    worst = graph.least_similar()
    assert worst is not None


def test_empty_envs():
    g = build_graph({})
    assert g.nodes == {}
    assert g.edges == []


def test_single_env():
    g = build_graph({"only": {"A": "1"}})
    assert len(g.nodes) == 1
    assert len(g.edges) == 0
