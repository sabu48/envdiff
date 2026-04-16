"""Tests for envdiff.filter."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.filter import filter_diff


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        missing_in_first={"DB_HOST": None, "AWS_KEY": None},
        missing_in_second={"APP_PORT": None},
        mismatched={"DB_PASS": ("secret", "other"), "AWS_REGION": ("us-east-1", "eu-west-1")},
        common={"SHARED": "val"},
    )


def test_no_filters_returns_all(result):
    filtered = filter_diff(result)
    assert set(filtered.missing_in_first) == {"DB_HOST", "AWS_KEY"}
    assert set(filtered.missing_in_second) == {"APP_PORT"}
    assert set(filtered.mismatched) == {"DB_PASS", "AWS_REGION"}


def test_pattern_filters_keys(result):
    filtered = filter_diff(result, patterns=["DB_*"])
    assert set(filtered.missing_in_first) == {"DB_HOST"}
    assert filtered.missing_in_second == {}
    assert set(filtered.mismatched) == {"DB_PASS"}


def test_category_filter_only_mismatched(result):
    filtered = filter_diff(result, categories=["mismatched"])
    assert filtered.missing_in_first == {}
    assert filtered.missing_in_second == {}
    assert set(filtered.mismatched) == {"DB_PASS", "AWS_REGION"}


def test_pattern_and_category_combined(result):
    filtered = filter_diff(result, patterns=["AWS_*"], categories=["missing_in_first", "mismatched"])
    assert set(filtered.missing_in_first) == {"AWS_KEY"}
    assert filtered.missing_in_second == {}
    assert set(filtered.mismatched) == {"AWS_REGION"}


def test_pattern_no_match_returns_empty(result):
    filtered = filter_diff(result, patterns=["NONEXISTENT_*"])
    assert filtered.missing_in_first == {}
    assert filtered.missing_in_second == {}
    assert filtered.mismatched == {}


def test_common_preserved(result):
    filtered = filter_diff(result, categories=["mismatched"])
    assert filtered.common == {"SHARED": "val"}
