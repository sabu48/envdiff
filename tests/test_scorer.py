"""Tests for envdiff.scorer."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.scorer import score, score_many, SimilarityScore


def _result(
    matching=None, mismatched=None, missing_in_first=None, missing_in_second=None
) -> DiffResult:
    return DiffResult(
        matching=matching or {},
        mismatched=mismatched or {},
        missing_in_first=missing_in_first or [],
        missing_in_second=missing_in_second or [],
    )


def test_identical_envs_score_one():
    r = _result(matching={"A": "1", "B": "2"})
    s = score(r)
    assert s.key_overlap == 1.0
    assert s.value_match == 1.0
    assert s.overall == 1.0


def test_no_common_keys_score_zero():
    r = _result(missing_in_first=["B"], missing_in_second=["A"])
    s = score(r)
    assert s.key_overlap == 0.0
    assert s.value_match == 1.0  # no common keys → defaults to 1.0
    assert s.overall == 0.5


def test_all_mismatched_value_match_zero():
    r = _result(mismatched={"A": {"first": "1", "second": "2"}, "B": {"first": "x", "second": "y"}})
    s = score(r)
    assert s.key_overlap == 1.0
    assert s.value_match == 0.0
    assert s.overall == 0.5


def test_partial_overlap():
    r = _result(
        matching={"A": "1"},
        mismatched={"B": {"first": "2", "second": "3"}},
        missing_in_second=["C"],
    )
    s = score(r)
    assert s.total_keys == 3
    assert s.common_keys == 2
    assert s.matching_values == 1
    assert s.key_overlap == pytest.approx(2 / 3, rel=1e-4)
    assert s.value_match == pytest.approx(0.5, rel=1e-4)


def test_empty_result():
    r = _result()
    s = score(r)
    assert s.total_keys == 0
    assert s.overall == 1.0


def test_score_many_returns_dict():
    r1 = _result(matching={"X": "1"})
    r2 = _result(mismatched={"X": {"first": "1", "second": "2"}})
    results = score_many({"pair_a": r1, "pair_b": r2})
    assert set(results.keys()) == {"pair_a", "pair_b"}
    assert isinstance(results["pair_a"], SimilarityScore)
    assert results["pair_a"].overall == 1.0
    assert results["pair_b"].overall == 0.5


def test_str_representation():
    r = _result(matching={"A": "1"})
    s = score(r)
    text = str(s)
    assert "overall=" in text
    assert "key_overlap=" in text
    assert "value_match=" in text
