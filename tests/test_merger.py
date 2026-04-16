"""Tests for envdiff.merger."""
import pytest
from envdiff.merger import merge, MergeResult


ENV_A = {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"}
ENV_B = {"HOST": "prodhost", "PORT": "5432", "SECRET": "abc"}
ENV_C = {"HOST": "staghost", "EXTRA": "1"}


def test_merge_no_conflicts():
    result = merge({"a": {"X": "1"}, "b": {"Y": "2"}})
    assert result.merged == {"X": "1", "Y": "2"}
    assert not result.has_conflicts()


def test_merge_last_strategy_wins():
    result = merge({"a": ENV_A, "b": ENV_B}, strategy="last")
    assert result.merged["HOST"] == "prodhost"


def test_merge_first_strategy_wins():
    result = merge({"a": ENV_A, "b": ENV_B}, strategy="first")
    assert result.merged["HOST"] == "localhost"


def test_merge_conflict_detected():
    result = merge({"a": ENV_A, "b": ENV_B})
    assert "HOST" in result.conflicts
    assert result.has_conflicts()


def test_merge_no_conflict_same_value():
    result = merge({"a": ENV_A, "b": ENV_B})
    assert "PORT" not in result.conflicts


def test_merge_three_sources():
    result = merge({"a": ENV_A, "b": ENV_B, "c": ENV_C}, strategy="last")
    assert result.merged["HOST"] == "staghost"
    assert "HOST" in result.conflicts


def test_sources_recorded():
    result = merge({"a": ENV_A, "b": ENV_B})
    assert result.sources == ["a", "b"]


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        merge({"a": ENV_A}, strategy="random")


def test_conflict_summary_no_conflicts():
    result = merge({"a": {"K": "v"}, "b": {"K": "v"}})
    assert result.conflict_summary() == "No conflicts."


def test_conflict_summary_with_conflicts():
    result = merge({"a": ENV_A, "b": ENV_B})
    summary = result.conflict_summary()
    assert "conflict" in summary
    assert "HOST" in summary
