"""Tests for envdiff.pinner."""
import json
from pathlib import Path

import pytest

from envdiff.pinner import PinResult, check_pin, load_pin, pin, save_pin


@pytest.fixture()
def base_env():
    return {"DB_HOST": "localhost", "DB_PORT": "5432", "SECRET": "abc"}


def test_pin_returns_copy(base_env):
    result = pin(base_env)
    assert result == base_env
    assert result is not base_env


def test_save_and_load_roundtrip(tmp_path, base_env):
    p = tmp_path / "env.pin"
    save_pin(base_env, p)
    loaded = load_pin(p)
    assert loaded == base_env


def test_save_creates_valid_json(tmp_path, base_env):
    p = tmp_path / "env.pin"
    save_pin(base_env, p)
    data = json.loads(p.read_text())
    assert data["DB_HOST"] == "localhost"


def test_load_converts_null_to_none(tmp_path):
    p = tmp_path / "env.pin"
    p.write_text(json.dumps({"KEY": None}))
    loaded = load_pin(p)
    assert loaded["KEY"] is None


def test_check_pin_no_deviations(base_env):
    result = check_pin(base_env, dict(base_env))
    assert not result.has_deviations()
    assert result.summary() == "no deviations"


def test_check_pin_detects_value_change(base_env):
    current = dict(base_env)
    current["DB_HOST"] = "remotehost"
    result = check_pin(base_env, current)
    assert result.has_deviations()
    assert "DB_HOST" in result.deviations
    assert result.deviations["DB_HOST"] == ("localhost", "remotehost")


def test_check_pin_new_key(base_env):
    current = dict(base_env)
    current["NEW_KEY"] = "value"
    result = check_pin(base_env, current)
    assert "NEW_KEY" in result.new_keys


def test_check_pin_removed_key(base_env):
    current = {k: v for k, v in base_env.items() if k != "SECRET"}
    result = check_pin(base_env, current)
    assert "SECRET" in result.removed_keys


def test_summary_lists_all_categories(base_env):
    current = {"DB_HOST": "changed", "EXTRA": "new"}
    result = check_pin(base_env, current)
    s = result.summary()
    assert "deviated" in s
    assert "new" in s
    assert "removed" in s
