"""Tests for envdiff.profiler."""
import pytest
from pathlib import Path
from envdiff.profiler import profile, ProfileResult


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> str:
    p.write_text(content)
    return str(p)


def test_profile_returns_profile_result(tmp):
    path = _write(tmp / ".env", "KEY=value\n")
    result = profile(path)
    assert isinstance(result, ProfileResult)


def test_total_keys(tmp):
    path = _write(tmp / ".env", "A=1\nB=2\nC=3\n")
    assert profile(path).total_keys == 3


def test_empty_keys_detected(tmp):
    path = _write(tmp / ".env", "A=\nB=hello\n")
    result = profile(path)
    assert "A" in result.empty_keys
    assert "B" not in result.empty_keys


def test_no_issues_clean_file(tmp):
    path = _write(tmp / ".env", "FOO=bar\nBAZ=qux\n")
    assert not profile(path).has_issues()


def test_long_value_flagged(tmp):
    long_val = "x" * 300
    path = _write(tmp / ".env", f"SECRET={long_val}\n")
    result = profile(path, max_value_len=256)
    assert "SECRET" in result.long_keys


def test_short_value_not_flagged(tmp):
    path = _write(tmp / ".env", "KEY=short\n")
    assert profile(path).long_keys == []


def test_duplicate_keys_detected(tmp):
    path = _write(tmp / ".env", "A=1\nA=2\nB=3\n")
    result = profile(path)
    assert "A" in result.duplicate_keys
    assert "B" not in result.duplicate_keys


def test_summary_string(tmp):
    path = _write(tmp / ".env", "A=\nB=hello\n")
    s = profile(path).summary()
    assert "total=" in s
    assert "empty=" in s


def test_key_lengths(tmp):
    path = _write(tmp / ".env", "FOO=hello\n")
    result = profile(path)
    assert result.key_lengths["FOO"] == 5
