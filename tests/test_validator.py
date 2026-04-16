"""Tests for envdiff.validator."""
import pytest
from envdiff.validator import KeySchema, ValidationResult, validate


@pytest.fixture
def env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "PORT": "8080",
        "DEBUG": "true",
        "SECRET_KEY": "abc123",
    }


def test_valid_env_passes(env):
    schema = KeySchema(required={"DATABASE_URL", "PORT"})
    result = validate(env, schema)
    assert result.is_valid


def test_missing_required_key(env):
    schema = KeySchema(required={"DATABASE_URL", "MISSING_KEY"})
    result = validate(env, schema)
    assert not result.is_valid
    assert "MISSING_KEY" in result.missing_required


def test_empty_value_treated_as_missing(env):
    env["PORT"] = ""
    schema = KeySchema(required={"PORT"})
    result = validate(env, schema)
    assert "PORT" in result.missing_required


def test_none_value_treated_as_missing(env):
    env["DEBUG"] = None
    schema = KeySchema(required={"DEBUG"})
    result = validate(env, schema)
    assert "DEBUG" in result.missing_required


def test_pattern_valid(env):
    schema = KeySchema(patterns={"PORT": r"\d+"})
    result = validate(env, schema)
    assert result.is_valid


def test_pattern_invalid(env):
    schema = KeySchema(patterns={"PORT": r"[a-z]+"})
    result = validate(env, schema)
    assert not result.is_valid
    assert "PORT" in result.invalid_values


def test_pattern_skipped_for_missing_key(env):
    schema = KeySchema(patterns={"NOT_PRESENT": r"\d+"})
    result = validate(env, schema)
    assert result.is_valid


def test_summary_all_pass(env):
    schema = KeySchema(required={"PORT"})
    result = validate(env, schema)
    assert result.summary() == "All validations passed."


def test_summary_with_errors(env):
    schema = KeySchema(required={"MISSING"}, patterns={"PORT": r"[a-z]+"})
    result = validate(env, schema)
    summary = result.summary()
    assert "MISSING" in summary
    assert "PORT" in summary
