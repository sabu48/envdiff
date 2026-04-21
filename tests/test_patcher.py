"""Tests for envdiff.patcher."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import pytest

from envdiff.comparator import DiffResult, compare
from envdiff.patcher import PatchResult, patch, write_patch


@pytest.fixture()
def diff() -> DiffResult:
    first = {"A": "1", "B": "old", "C": "3"}
    second = {"A": "1", "B": "new", "D": "4"}
    return compare(first, second)


def test_patch_adds_missing_key(diff: DiffResult) -> None:
    base = {"A": "1", "B": "old", "C": "3"}
    result = patch(base, diff, add_missing=True, update_mismatched=False)
    assert "D" in result.patched
    assert result.patched["D"] == "4"
    assert "D" in result.added


def test_patch_updates_mismatched_key(diff: DiffResult) -> None:
    base = {"A": "1", "B": "old", "C": "3"}
    result = patch(base, diff, add_missing=False, update_mismatched=True)
    assert result.patched["B"] == "new"
    assert "B" in result.updated


def test_patch_does_not_add_when_disabled(diff: DiffResult) -> None:
    base = {"A": "1", "B": "old", "C": "3"}
    result = patch(base, diff, add_missing=False, update_mismatched=False)
    assert "D" not in result.patched
    assert result.added == []
    assert result.updated == []


def test_patch_skips_specified_keys(diff: DiffResult) -> None:
    base = {"A": "1", "B": "old", "C": "3"}
    result = patch(base, diff, add_missing=True, update_mismatched=True, skip_keys=["D", "B"])
    assert "D" not in result.patched
    assert result.patched["B"] == "old"
    assert "D" in result.skipped
    assert "B" in result.skipped


def test_patch_has_changes_true(diff: DiffResult) -> None:
    base = {"A": "1", "B": "old", "C": "3"}
    result = patch(base, diff)
    assert result.has_changes()


def test_patch_has_changes_false() -> None:
    first = {"A": "1"}
    second = {"A": "1"}
    d = compare(first, second)
    result = patch(first, d)
    assert not result.has_changes()


def test_summary_no_changes() -> None:
    first = {"X": "1"}
    d = compare(first, first)
    result = patch(first, d)
    assert result.summary() == "no changes"


def test_summary_lists_added_and_updated(diff: DiffResult) -> None:
    base = {"A": "1", "B": "old", "C": "3"}
    result = patch(base, diff)
    s = result.summary()
    assert "added" in s
    assert "updated" in s


def test_write_patch_creates_file(tmp_path: Path) -> None:
    out = tmp_path / "out.env"
    patched = {"KEY": "value", "EMPTY": None, "SPACED": "hello world"}
    write_patch(out, patched)
    content = out.read_text()
    assert "KEY=value" in content
    assert "EMPTY=" in content
    assert 'SPACED="hello world"' in content


def test_write_patch_roundtrip(tmp_path: Path) -> None:
    from envdiff.parser import parse_env_file

    out = tmp_path / "patched.env"
    patched = {"FOO": "bar", "BAZ": "qux"}
    write_patch(out, patched)
    parsed = parse_env_file(out)
    assert parsed["FOO"] == "bar"
    assert parsed["BAZ"] == "qux"
