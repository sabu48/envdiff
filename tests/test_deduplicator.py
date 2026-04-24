"""Tests for envdiff.deduplicator."""
import pytest
from envdiff.deduplicator import deduplicate, DeduplicateResult


@pytest.fixture
def envs():
    return [
        {"HOST": "localhost", "PORT": "5432", "DEBUG": "true"},
        {"HOST": "prod.example.com", "PORT": "5432", "SECRET": "abc"},
        {"HOST": "staging.example.com", "SECRET": "xyz", "EXTRA": "1"},
    ]


def test_returns_deduplicate_result(envs):
    result = deduplicate(envs)
    assert isinstance(result, DeduplicateResult)


def test_last_strategy_picks_last_value(envs):
    result = deduplicate(envs, strategy="last")
    assert result.resolved["HOST"] == "staging.example.com"
    assert result.resolved["SECRET"] == "xyz"


def test_first_strategy_picks_first_value(envs):
    result = deduplicate(envs, strategy="first")
    assert result.resolved["HOST"] == "localhost"
    assert result.resolved["SECRET"] == "abc"


def test_all_keys_present_in_resolved(envs):
    result = deduplicate(envs, strategy="last")
    assert set(result.resolved.keys()) == {"HOST", "PORT", "DEBUG", "SECRET", "EXTRA"}


def test_last_strategy_no_conflicts(envs):
    result = deduplicate(envs, strategy="last")
    assert not result.has_conflicts()
    assert result.conflicts == {}


def test_strict_strategy_detects_conflicts(envs):
    result = deduplicate(envs, strategy="strict")
    assert result.has_conflicts()
    assert "HOST" in result.conflicts
    assert "SECRET" in result.conflicts


def test_strict_strategy_no_conflict_for_same_value(envs):
    result = deduplicate(envs, strategy="strict")
    # PORT is "5432" in both envs that define it
    assert "PORT" not in result.conflicts


def test_strict_strategy_uses_first_value(envs):
    result = deduplicate(envs, strategy="strict")
    assert result.resolved["HOST"] == "localhost"


def test_sources_track_winning_index_last(envs):
    result = deduplicate(envs, strategy="last")
    assert result.sources["HOST"] == 2
    assert result.sources["DEBUG"] == 0


def test_sources_track_winning_index_first(envs):
    result = deduplicate(envs, strategy="first")
    assert result.sources["HOST"] == 0
    assert result.sources["EXTRA"] == 2


def test_ignore_keys_not_in_conflicts():
    a = {"TOKEN": "aaa", "APP": "foo"}
    b = {"TOKEN": "bbb", "APP": "foo"}
    result = deduplicate([a, b], strategy="strict", ignore_keys=["TOKEN"])
    assert "TOKEN" not in result.conflicts


def test_none_value_handled():
    a = {"KEY": None}
    b = {"KEY": "value"}
    result = deduplicate([a, b], strategy="strict")
    assert result.has_conflicts()
    assert None in result.conflicts["KEY"]


def test_invalid_strategy_raises():
    with pytest.raises(ValueError, match="Unknown strategy"):
        deduplicate([{"A": "1"}], strategy="random")


def test_conflict_summary_no_conflicts():
    result = deduplicate([{"A": "1"}, {"A": "1"}], strategy="strict")
    assert result.conflict_summary() == "No conflicts."


def test_conflict_summary_lists_keys():
    a = {"X": "alpha"}
    b = {"X": "beta"}
    result = deduplicate([a, b], strategy="strict")
    summary = result.conflict_summary()
    assert "X" in summary
    assert "alpha" in summary
    assert "beta" in summary
