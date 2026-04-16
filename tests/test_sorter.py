"""Tests for envdiff.sorter."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.sorter import SortOrder, all_diff_keys, sort_diff


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        missing_in_first={"ZEBRA": None},
        missing_in_second={"ALPHA": None},
        mismatched={"MANGO": ("old", "new")},
        common={"SHARED": "value"},
    )


def test_all_diff_keys_sorted(result):
    keys = all_diff_keys(result)
    assert keys == ["ALPHA", "MANGO", "ZEBRA"]


def test_sort_by_key(result):
    entries = sort_diff(result, SortOrder.KEY)
    keys = [k for k, _ in entries]
    assert keys == sorted(keys)


def test_sort_by_severity_order(result):
    entries = sort_diff(result, SortOrder.SEVERITY)
    categories = [cat for _, cat in entries]
    # missing_in_second (0) should come before missing_in_first (1) before mismatched (2)
    severity_indices = []
    seen: dict = {}
    order_map = {"missing_in_second": 0, "missing_in_first": 1, "mismatched": 2}
    for cat in categories:
        severity_indices.append(order_map[cat])
    assert severity_indices == sorted(severity_indices)


def test_sort_returns_correct_categories(result):
    entries = sort_diff(result)
    cat_map = dict(entries)
    assert cat_map["ALPHA"] == "missing_in_second"
    assert cat_map["ZEBRA"] == "missing_in_first"
    assert cat_map["MANGO"] == "mismatched"


def test_empty_result():
    empty = DiffResult(
        missing_in_first={},
        missing_in_second={},
        mismatched={},
        common={},
    )
    assert all_diff_keys(empty) == []
    assert sort_diff(empty) == []


def test_only_mismatched():
    r = DiffResult(
        missing_in_first={},
        missing_in_second={},
        mismatched={"KEY": ("a", "b")},
        common={},
    )
    entries = sort_diff(r, SortOrder.SEVERITY)
    assert entries == [("KEY", "mismatched")]
