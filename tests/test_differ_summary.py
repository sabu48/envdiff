"""Tests for envdiff.differ_summary."""
import os
import pytest
from pathlib import Path

from envdiff.differ_summary import build_report, DiffSummaryReport


@pytest.fixture
def tmp_envs(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_build_report_returns_diff_summary_report(tmp_envs):
    a = tmp_envs("a.env", "KEY=1\nSHARED=x\n")
    b = tmp_envs("b.env", "KEY=1\nSHARED=x\n")
    report = build_report({"a": a, "b": b})
    assert isinstance(report, DiffSummaryReport)


def test_no_differences_when_identical(tmp_envs):
    a = tmp_envs("a.env", "KEY=1\n")
    b = tmp_envs("b.env", "KEY=1\n")
    report = build_report({"a": a, "b": b})
    assert not report.has_any_differences


def test_has_differences_when_mismatched(tmp_envs):
    a = tmp_envs("a.env", "KEY=1\n")
    b = tmp_envs("b.env", "KEY=2\n")
    report = build_report({"a": a, "b": b})
    assert report.has_any_differences


def test_env_names_present(tmp_envs):
    a = tmp_envs("a.env", "KEY=1\n")
    b = tmp_envs("b.env", "KEY=1\n")
    report = build_report({"alpha": a, "beta": b})
    names = report.env_names()
    assert "alpha" in names
    assert "beta" in names


def test_summary_total_keys(tmp_envs):
    a = tmp_envs("a.env", "A=1\nB=2\n")
    b = tmp_envs("b.env", "A=1\nC=3\n")
    report = build_report({"a": a, "b": b})
    assert report.summary.total_keys >= 2


def test_diffs_keyed_by_pair(tmp_envs):
    a = tmp_envs("a.env", "X=1\n")
    b = tmp_envs("b.env", "X=2\n")
    report = build_report({"a": a, "b": b})
    assert len(report.diffs) >= 1
