"""Tests for envdiff.normalizer."""

import pytest
from envdiff.normalizer import normalize, normalize_many, NormalizeResult


@pytest.fixture
def env():
    return {
        "DATABASE_URL": '"postgres://localhost/db"',
        "api_key": "  secret123  ",
        "Port": "5432",
        "EMPTY": "",
        "NONE_VAL": None,
    }


def test_normalize_returns_normalize_result(env):
    result = normalize(env)
    assert isinstance(result, NormalizeResult)


def test_original_is_unchanged_copy(env):
    result = normalize(env)
    assert result.original == env
    assert result.original is not env  # it's a copy


def test_value_outer_double_quotes_stripped(env):
    result = normalize(env)
    assert result.normalized["DATABASE_URL"] == "postgres://localhost/db"


def test_value_whitespace_stripped(env):
    result = normalize(env)
    assert result.normalized["API_KEY"] == "secret123"


def test_key_uppercased(env):
    result = normalize(env)
    assert "API_KEY" in result.normalized
    assert "api_key" not in result.normalized


def test_key_case_change_recorded_in_changes(env):
    result = normalize(env)
    assert "API_KEY" in result.changes
    assert "api_key" in result.changes["API_KEY"]


def test_value_change_recorded_in_changes(env):
    result = normalize(env)
    assert "DATABASE_URL" in result.changes


def test_no_change_key_not_in_changes(env):
    result = normalize(env)
    # PORT is already upper-case; value '5432' needs no stripping
    assert "PORT" not in result.changes


def test_empty_value_preserved(env):
    result = normalize(env)
    assert result.normalized["EMPTY"] == ""


def test_none_value_preserved(env):
    result = normalize(env)
    assert result.normalized["NONE_VAL"] is None


def test_single_quote_stripped():
    result = normalize({"KEY": "'hello'"})
    assert result.normalized["KEY"] == "hello"


def test_mismatched_quotes_not_stripped():
    result = normalize({"KEY": "'hello\""})
    assert result.normalized["KEY"] == "'hello\""


def test_normalize_many_returns_per_name_results():
    envs = {
        "staging": {"db_url": '"postgres://staging"'},
        "prod": {"DB_URL": "postgres://prod"},
    }
    results = normalize_many(envs)
    assert set(results.keys()) == {"staging", "prod"}
    assert results["staging"].normalized["DB_URL"] == "postgres://staging"
    assert results["prod"].normalized["DB_URL"] == "postgres://prod"
