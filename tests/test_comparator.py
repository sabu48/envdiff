"""Tests for envdiff.comparator module."""

import pytest
from envdiff.comparator import compare, DiffResult


def test_identical_envs_no_differences():
    a = {"HOST": "localhost", "PORT": "5432"}
    b = {"HOST": "localhost", "PORT": "5432"}
    result = compare(a, b)
    assert not result.has_differences


def test_missing_key_in_second():
    a = {"HOST": "localhost", "PORT": "5432"}
    b = {"HOST": "localhost"}
    result = compare(a, b)
    assert "PORT" in result.missing_in_second
    assert not result.missing_in_first
    assert not result.mismatched


def test_missing_key_in_first():
    a = {"HOST": "localhost"}
    b = {"HOST": "localhost", "PORT": "5432"}
    result = compare(a, b)
    assert "PORT" in result.missing_in_first
    assert not result.missing_in_second
    assert not result.mismatched


def test_mismatched_values():
    a = {"HOST": "localhost", "PORT": "5432"}
    b = {"HOST": "production.db", "PORT": "5432"}
    result = compare(a, b)
    assert "HOST" in result.mismatched
    assert result.mismatched["HOST"] == {"first": "localhost", "second": "production.db"}
    assert not result.missing_in_first
    assert not result.missing_in_second


def test_empty_value_vs_none():
    a = {"KEY": ""}
    b = {"KEY": None}
    result = compare(a, b)
    assert "KEY" in result.mismatched


def test_both_empty_dicts():
    result = compare({}, {})
    assert not result.has_differences


def test_summary_no_differences():
    result = compare({"A": "1"}, {"A": "1"})
    assert "No differences found" in result.summary()


def test_summary_labels():
    a = {"DB": "dev"}
    b = {"DB": "prod"}
    result = compare(a, b)
    summary = result.summary(label_first=".env.dev", label_second=".env.prod")
    assert "DB" in summary
    assert "dev" in summary
    assert "prod" in summary


def test_has_differences_flag():
    result = DiffResult(missing_in_second=["FOO"])
    assert result.has_differences

    result2 = DiffResult()
    assert not result2.has_differences
