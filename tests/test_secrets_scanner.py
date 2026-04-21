"""Tests for envdiff.secrets_scanner."""
import pytest
from envdiff.secrets_scanner import scan, ScanResult, SecretHit, _looks_like_real_secret


@pytest.fixture()
def clean_env():
    return {
        "APP_NAME": "myapp",
        "DEBUG": "true",
        "PORT": "8080",
    }


@pytest.fixture()
def dirty_env():
    return {
        "APP_NAME": "myapp",
        "DB_PASSWORD": "supersecretpassword123",
        "API_KEY": "abcdef1234567890",
        "AUTH_TOKEN": "changeme",  # placeholder — should NOT trigger
        "PRIVATE_KEY": "<your-private-key>",  # placeholder
    }


def test_clean_env_returns_no_hits(clean_env):
    result = scan(clean_env)
    assert result.clean
    assert result.hits == []


def test_scanned_count_matches_env_size(clean_env):
    result = scan(clean_env)
    assert result.scanned == len(clean_env)


def test_dirty_env_detects_password(dirty_env):
    result = scan(dirty_env)
    keys = [h.key for h in result.hits]
    assert "DB_PASSWORD" in keys


def test_dirty_env_detects_api_key(dirty_env):
    result = scan(dirty_env)
    keys = [h.key for h in result.hits]
    assert "API_KEY" in keys


def test_placeholder_not_flagged(dirty_env):
    result = scan(dirty_env)
    keys = [h.key for h in result.hits]
    assert "AUTH_TOKEN" not in keys
    assert "PRIVATE_KEY" not in keys


def test_hit_contains_value_preview(dirty_env):
    result = scan(dirty_env)
    hit = next(h for h in result.hits if h.key == "DB_PASSWORD")
    assert hit.value_preview.startswith("supe")
    assert "****" in hit.value_preview


def test_summary_clean(clean_env):
    result = scan(clean_env)
    assert "No exposed secrets" in result.summary()


def test_summary_dirty(dirty_env):
    result = scan(dirty_env)
    s = result.summary()
    assert "potential secret" in s
    assert "DB_PASSWORD" in s


def test_looks_like_real_secret_short_value():
    assert not _looks_like_real_secret("abc")


def test_looks_like_real_secret_none():
    assert not _looks_like_real_secret(None)


def test_looks_like_real_secret_valid():
    assert _looks_like_real_secret("verylongsecretvalue")


def test_empty_value_not_flagged():
    result = scan({"API_KEY": ""})
    assert result.clean
