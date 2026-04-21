"""Tests for envdiff.duplicates."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.duplicates import DuplicateResult, find_duplicates, find_duplicates_many


@pytest.fixture
def tmp(tmp_path: Path) -> Path:
    return tmp_path


def _write(p: Path, content: str) -> Path:
    p.write_text(content, encoding="utf-8")
    return p


def test_no_duplicates_clean_file(tmp: Path) -> None:
    f = _write(tmp / ".env", "FOO=bar\nBAZ=qux\n")
    result = find_duplicates(f)
    assert not result.has_duplicates
    assert result.duplicates == {}


def test_single_duplicate_key(tmp: Path) -> None:
    f = _write(tmp / ".env", "FOO=first\nBAR=ok\nFOO=second\n")
    result = find_duplicates(f)
    assert result.has_duplicates
    assert "FOO" in result.duplicates
    assert result.duplicates["FOO"] == [1, 3]


def test_triple_occurrence(tmp: Path) -> None:
    f = _write(tmp / ".env", "KEY=a\nKEY=b\nOTHER=x\nKEY=c\n")
    result = find_duplicates(f)
    assert result.duplicates["KEY"] == [1, 2, 4]


def test_comments_and_blanks_ignored(tmp: Path) -> None:
    content = "# FOO=comment\nFOO=real\n\nFOO=dup\n"
    f = _write(tmp / ".env", content)
    result = find_duplicates(f)
    assert result.duplicates["FOO"] == [2, 4]


def test_export_prefix_stripped(tmp: Path) -> None:
    f = _write(tmp / ".env", "export FOO=first\nexport FOO=second\n")
    result = find_duplicates(f)
    assert "FOO" in result.duplicates
    assert result.duplicates["FOO"] == [1, 2]


def test_summary_no_duplicates(tmp: Path) -> None:
    f = _write(tmp / ".env", "A=1\nB=2\n")
    result = find_duplicates(f)
    assert "no duplicate" in result.summary()


def test_summary_with_duplicates(tmp: Path) -> None:
    f = _write(tmp / ".env", "X=1\nX=2\n")
    result = find_duplicates(f)
    s = result.summary()
    assert "1 duplicate" in s
    assert "X" in s
    assert "1, 2" in s


def test_find_duplicates_many(tmp: Path) -> None:
    f1 = _write(tmp / "a.env", "FOO=1\nFOO=2\n")
    f2 = _write(tmp / "b.env", "BAR=x\nBAZ=y\n")
    results = find_duplicates_many([f1, f2])
    assert len(results) == 2
    assert results[str(f1)].has_duplicates
    assert not results[str(f2)].has_duplicates


def test_result_path_stored(tmp: Path) -> None:
    f = _write(tmp / "test.env", "A=1\n")
    result = find_duplicates(f)
    assert result.path == str(f)
