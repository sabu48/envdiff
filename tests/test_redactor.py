"""Tests for envdiff.redactor."""
import re
import pytest
from envdiff.redactor import redact_env, redact_diff, REDACTED, _is_sensitive


def test_is_sensitive_password():
    assert _is_sensitive("DB_PASSWORD")


def test_is_sensitive_token():
    assert _is_sensitive("GITHUB_TOKEN")


def test_is_sensitive_api_key():
    assert _is_sensitive("STRIPE_API_KEY")


def test_not_sensitive_plain_key():
    assert not _is_sensitive("APP_NAME")


def test_redact_env_replaces_sensitive():
    env = {"DB_PASSWORD": "s3cr3t", "APP_NAME": "myapp", "API_TOKEN": "abc123"}
    result = redact_env(env)
    assert result["DB_PASSWORD"] == REDACTED
    assert result["API_TOKEN"] == REDACTED
    assert result["APP_NAME"] == "myapp"


def test_redact_env_preserves_none():
    env = {"DB_PASSWORD": None, "APP_NAME": None}
    result = redact_env(env)
    assert result["DB_PASSWORD"] is None
    assert result["APP_NAME"] is None


def test_redact_env_extra_patterns():
    extra = [re.compile(r"internal", re.IGNORECASE)]
    env = {"INTERNAL_URL": "http://internal", "PUBLIC_URL": "http://public"}
    result = redact_env(env, extra_patterns=extra)
    assert result["INTERNAL_URL"] == REDACTED
    assert result["PUBLIC_URL"] == "http://public"


def test_redact_diff_mismatched():
    diff = {
        "missing_in_second": ["FOO"],
        "missing_in_first": [],
        "mismatched": {"DB_PASSWORD": ("old", "new"), "HOST": ("a", "b")},
        "matched": {},
    }
    result = redact_diff(diff)
    assert result["mismatched"]["DB_PASSWORD"] == (REDACTED, REDACTED)
    assert result["mismatched"]["HOST"] == ("a", "b")


def test_redact_diff_matched():
    diff = {
        "missing_in_second": [],
        "missing_in_first": [],
        "mismatched": {},
        "matched": {"SECRET_KEY": "abc", "PORT": "8080"},
    }
    result = redact_diff(diff)
    assert result["matched"]["SECRET_KEY"] == REDACTED
    assert result["matched"]["PORT"] == "8080"


def test_redact_diff_preserves_missing_lists():
    diff = {
        "missing_in_second": ["KEY_A"],
        "missing_in_first": ["KEY_B"],
        "mismatched": {},
        "matched": {},
    }
    result = redact_diff(diff)
    assert result["missing_in_second"] == ["KEY_A"]
    assert result["missing_in_first"] == ["KEY_B"]
