"""Tests for envdiff.linter."""
import pytest
from pathlib import Path
from envdiff.linter import lint_file, LintResult


@pytest.fixture
def tmp(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def test_clean_file_has_no_issues(tmp):
    p = tmp("clean.env", "DB_HOST=localhost\nDB_PORT=5432\n")
    result = lint_file(p)
    assert result.ok
    assert result.issues == []


def test_lowercase_key_flagged(tmp):
    p = tmp("bad.env", "db_host=localhost\n")
    result = lint_file(p)
    codes = [i.code for i in result.issues]
    assert "E002" in codes


def test_missing_equals_flagged(tmp):
    p = tmp("bad.env", "OEQUALSSIGN\n")
    result = lint_file(p)
    codes = [i.code for i in result.issues]
    assert "E001" in codes


def test_duplicate_key_flagged(tmp):
    p = tmp("dup.env", "FOO=1\nFOO=2\n")
    result = lint_file(p)
    codes = [i.code for i in result.issues]
    assert "W001" in codes


def test_trailing_whitespace_in_value(tmp):
    p = tmp("ws.env", "FOO=bar   \n")
    result = lint_file(p)
    codes = [i.code for i in result.issues]
    assert "W002" in codes


def test_comments_and_blank_lines_ignored(tmp):
    p = tmp("comments.env", "# comment\n\nFOO=bar\n")
    result = lint_file(p)
    assert result.ok


def test_summary_ok(tmp):
    p = tmp("ok.env", "FOO=1\n")
    result = lint_file(p)
    assert "no issues" in result.summary()


def test_summary_with_issues(tmp):
    p = tmp("bad.env", "foo=1\n")
    result = lint_file(p)
    s = result.summary()
    assert "E002" in s
    assert "1 issue" in s
