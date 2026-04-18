"""Tests for envdiff.baseline."""
import json
import pytest
from pathlib import Path

from envdiff.baseline import save_baseline, load_baseline, compare_to_baseline


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


def test_save_and_load_roundtrip(tmp):
    env = {"KEY": "value", "EMPTY": "", "NONE_KEY": None}
    p = str(tmp / "baseline.json")
    save_baseline(env, p)
    loaded = load_baseline(p)
    assert loaded == env


def test_save_creates_valid_json(tmp):
    env = {"A": "1", "B": "2"}
    p = str(tmp / "baseline.json")
    save_baseline(env, p)
    data = json.loads(Path(p).read_text())
    assert data == env


def test_load_converts_null_to_none(tmp):
    p = tmp / "baseline.json"
    p.write_text(json.dumps({"X": None, "Y": "hello"}))
    result = load_baseline(str(p))
    assert result["X"] is None
    assert result["Y"] == "hello"


def test_compare_identical_no_differences(tmp):
    env = {"HOST": "localhost", "PORT": "5432"}
    p = str(tmp / "baseline.json")
    save_baseline(env, p)
    diff = compare_to_baseline(env, p)
    assert not diff.missing_in_first
    assert not diff.missing_in_second
    assert not diff.mismatched


def test_compare_detects_new_key(tmp):
    baseline = {"HOST": "localhost"}
    current = {"HOST": "localhost", "NEW_KEY": "value"}
    p = str(tmp / "baseline.json")
    save_baseline(baseline, p)
    diff = compare_to_baseline(current, p)
    assert "NEW_KEY" in diff.missing_in_second


def test_compare_detects_removed_key(tmp):
    baseline = {"HOST": "localhost", "OLD_KEY": "old"}
    current = {"HOST": "localhost"}
    p = str(tmp / "baseline.json")
    save_baseline(baseline, p)
    diff = compare_to_baseline(current, p)
    assert "OLD_KEY" in diff.missing_in_first


def test_compare_detects_changed_value(tmp):
    baseline = {"HOST": "localhost"}
    current = {"HOST": "production.example.com"}
    p = str(tmp / "baseline.json")
    save_baseline(baseline, p)
    diff = compare_to_baseline(current, p)
    assert "HOST" in diff.mismatched
