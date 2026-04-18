"""Tests for envdiff.drift."""
import json
import pytest
from pathlib import Path

from envdiff.drift import detect_drift, DriftReport


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


def _write_env(path: Path, content: str) -> str:
    path.write_text(content)
    return str(path)


def _write_baseline(path: Path, data: dict) -> str:
    path.write_text(json.dumps(data))
    return str(path)


def test_no_drift_when_identical(tmp):
    baseline = _write_baseline(tmp / "baseline.json", {"KEY": "val", "FOO": "bar"})
    env = _write_env(tmp / ".env", "KEY=val\nFOO=bar\n")
    report = detect_drift(baseline, env)
    assert not report.has_drift
    assert report.new_keys == []
    assert report.removed_keys == []
    assert report.changed_keys == []


def test_new_key_detected(tmp):
    baseline = _write_baseline(tmp / "baseline.json", {"KEY": "val"})
    env = _write_env(tmp / ".env", "KEY=val\nNEW=extra\n")
    report = detect_drift(baseline, env)
    assert report.has_drift
    assert "NEW" in report.new_keys
    assert report.removed_keys == []


def test_removed_key_detected(tmp):
    baseline = _write_baseline(tmp / "baseline.json", {"KEY": "val", "OLD": "gone"})
    env = _write_env(tmp / ".env", "KEY=val\n")
    report = detect_drift(baseline, env)
    assert report.has_drift
    assert "OLD" in report.removed_keys
    assert report.new_keys == []


def test_changed_value_detected(tmp):
    baseline = _write_baseline(tmp / "baseline.json", {"KEY": "old"})
    env = _write_env(tmp / ".env", "KEY=new\n")
    report = detect_drift(baseline, env)
    assert report.has_drift
    assert "KEY" in report.changed_keys


def test_summary_no_drift(tmp):
    baseline = _write_baseline(tmp / "baseline.json", {"A": "1"})
    env = _write_env(tmp / ".env", "A=1\n")
    report = detect_drift(baseline, env)
    assert report.summary() == "No drift detected."


def test_summary_with_drift(tmp):
    baseline = _write_baseline(tmp / "baseline.json", {"A": "1", "B": "2"})
    env = _write_env(tmp / ".env", "A=changed\nC=3\n")
    report = detect_drift(baseline, env)
    s = report.summary()
    assert "new" in s
    assert "removed" in s
    assert "changed" in s


def test_report_stores_paths(tmp):
    baseline = _write_baseline(tmp / "baseline.json", {"X": "1"})
    env = _write_env(tmp / ".env", "X=1\n")
    report = detect_drift(baseline, env)
    assert "baseline.json" in report.baseline_path
    assert ".env" in report.env_path
