"""Tests for envdiff.cli_lint."""
import pytest
from pathlib import Path
from envdiff.cli_lint import build_lint_parser, _run_lint


@pytest.fixture
def tmp_env(tmp_path):
    def _write(name: str, content: str) -> str:
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def _run(argv):
    parser = build_lint_parser()
    args = parser.parse_args(argv)
    return _run_lint(args)


def test_clean_file_exits_zero(tmp_env):
    p = tmp_env("a.env", "FOO=bar\nBAZ=1\n")
    assert _run([p]) == 0


def test_issues_without_strict_exits_zero(tmp_env):
    p = tmp_env("a.env", "foo=bar\n")
    assert _run([p]) == 0


def test_issues_with_strict_exits_one(tmp_env):
    p = tmp_env("a.env", "foo=bar\n")
    assert _run(["--strict", p]) == 1


def test_clean_with_strict_exits_zero(tmp_env):
    p = tmp_env("a.env", "FOO=bar\n")
    assert _run(["--strict", p]) == 0


def test_multiple_files(tmp_env):
    p1 = tmp_env("a.env", "FOO=1\n")
    p2 = tmp_env("b.env", "BAR=2\n")
    assert _run([p1, p2]) == 0


def test_quiet_suppresses_clean_output(tmp_env, capsys):
    p = tmp_env("a.env", "FOO=1\n")
    _run(["--quiet", p])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_quiet_still_shows_issues(tmp_env, capsys):
    p = tmp_env("a.env", "foo=1\n")
    _run(["--quiet", p])
    captured = capsys.readouterr()
    assert "E002" in captured.out
