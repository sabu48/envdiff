"""Tests for envdiff.grouper."""
import pytest

from envdiff.comparator import DiffResult
from envdiff.grouper import GroupReport, _extract_prefix, all_diff_keys, group_diff


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        missing_in_second=["DB_HOST", "DB_PORT", "APP_NAME"],
        missing_in_first=["AWS_KEY"],
        mismatched={"DB_PASS": ("secret", "other"), "APP_ENV": ("prod", "dev")},
    )


def test_extract_prefix_with_underscore():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_separator():
    assert _extract_prefix("NOPREFIX") is None


def test_extract_prefix_custom_separator():
    assert _extract_prefix("db.host", separator=".") == "db"


def test_all_diff_keys_sorted(result):
    keys = all_diff_keys(result)
    assert keys == sorted(keys)
    assert "DB_HOST" in keys
    assert "AWS_KEY" in keys
    assert "APP_ENV" in keys


def test_group_diff_creates_groups(result):
    report = group_diff(result)
    assert "DB" in report.all_prefixes()
    assert "APP" in report.all_prefixes()
    assert "AWS" in report.all_prefixes()


def test_group_diff_keys_for_db(result):
    report = group_diff(result)
    db_keys = report.keys_for("DB")
    assert "DB_HOST" in db_keys
    assert "DB_PORT" in db_keys
    assert "DB_PASS" in db_keys


def test_group_diff_ungrouped_when_no_prefix():
    r = DiffResult(
        missing_in_second=["NOPREFIX"],
        missing_in_first=[],
        mismatched={},
    )
    report = group_diff(r)
    assert "NOPREFIX" in report.ungrouped


def test_min_group_size_moves_small_groups_to_ungrouped(result):
    # AWS has only 1 key; with min_group_size=2 it should be ungrouped
    report = group_diff(result, min_group_size=2)
    assert "AWS" not in report.all_prefixes()
    assert "AWS_KEY" in report.ungrouped


def test_group_report_keys_for_missing_prefix(result):
    report = group_diff(result)
    assert report.keys_for("NONEXISTENT") == []


def test_empty_diff_produces_empty_report():
    r = DiffResult(missing_in_second=[], missing_in_first=[], mismatched={})
    report = group_diff(r)
    assert report.groups == {}
    assert report.ungrouped == []
