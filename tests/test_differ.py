"""Tests for envdiff.differ high-level pipeline."""
import pytest
from pathlib import Path

from envdiff.differ import diff_files, diff_many
from envdiff.sorter import SortOrder


@pytest.fixture()
def tmp_envs(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_diff_files_identical(tmp_envs):
    a = tmp_envs("a.env", "KEY=val\nFOO=bar\n")
    b = tmp_envs("b.env", "KEY=val\nFOO=bar\n")
    result = diff_files(a, b)
    assert result.missing_in_second == {}
    assert result.missing_in_first == {}
    assert result.mismatched == {}


def test_diff_files_missing_key(tmp_envs):
    a = tmp_envs("a.env", "KEY=val\nEXTRA=only_a\n")
    b = tmp_envs("b.env", "KEY=val\n")
    result = diff_files(a, b)
    assert "EXTRA" in result.missing_in_second


def test_diff_files_mismatched(tmp_envs):
    a = tmp_envs("a.env", "KEY=foo\n")
    b = tmp_envs("b.env", "KEY=bar\n")
    result = diff_files(a, b)
    assert "KEY" in result.mismatched


def test_diff_files_pattern_filter(tmp_envs):
    a = tmp_envs("a.env", "DB_HOST=localhost\nAPP_NAME=myapp\n")
    b = tmp_envs("b.env", "DB_HOST=prod\nAPP_NAME=myapp\n")
    result = diff_files(a, b, pattern="DB_*")
    assert "DB_HOST" in result.mismatched
    assert "APP_NAME" not in result.mismatched


def test_diff_files_sort_by_severity(tmp_envs):
    a = tmp_envs("a.env", "ONLY_A=1\nSHARED=x\n")
    b = tmp_envs("b.env", "ONLY_B=2\nSHARED=y\n")
    result = diff_files(a, b, sort=SortOrder.SEVERITY)
    # Just verify it returns a DiffResult without error
    assert result is not None


def test_diff_many_basic(tmp_envs):
    base = tmp_envs("base.env", "KEY=val\nFOO=base\n")
    env1 = tmp_envs("env1.env", "KEY=val\nFOO=one\n")
    env2 = tmp_envs("env2.env", "KEY=val\n")
    results = diff_many([base, env1, env2])
    assert len(results) == 2
    assert "FOO" in results[0].mismatched
    assert "FOO" in results[1].missing_in_second


def test_diff_many_requires_two_files(tmp_envs):
    a = tmp_envs("a.env", "KEY=val\n")
    with pytest.raises(ValueError):
        diff_many([a])


def test_diff_many_bad_baseline(tmp_envs):
    a = tmp_envs("a.env", "KEY=val\n")
    b = tmp_envs("b.env", "KEY=val\n")
    with pytest.raises(IndexError):
        diff_many([a, b], baseline=5)
