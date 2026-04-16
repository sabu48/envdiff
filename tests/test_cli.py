"""Tests for the CLI entry point."""
import json
import pytest
from pathlib import Path

from envdiff.cli import main


@pytest.fixture()
def tmp_env(tmp_path):
    """Factory that writes a .env file and returns its path."""
    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p
    return _write


def test_identical_files_exit_zero(tmp_env):
    a = tmp_env("a.env", "FOO=bar\nBAZ=qux\n")
    b = tmp_env("b.env", "FOO=bar\nBAZ=qux\n")
    assert main([str(a), str(b)]) == 0


def test_differences_exit_zero_without_flag(tmp_env):
    a = tmp_env("a.env", "FOO=bar\n")
    b = tmp_env("b.env", "FOO=different\n")
    assert main([str(a), str(b)]) == 0


def test_differences_exit_one_with_flag(tmp_env):
    a = tmp_env("a.env", "FOO=bar\n")
    b = tmp_env("b.env", "FOO=different\n")
    assert main([str(a), str(b), "--exit-code"]) == 1


def test_missing_file_returns_2(tmp_env, tmp_path):
    a = tmp_env("a.env", "FOO=bar\n")
    missing = tmp_path / "ghost.env"
    assert main([str(a), str(missing)]) == 2


def test_json_output_is_valid(tmp_env, capsys):
    a = tmp_env("a.env", "FOO=bar\nONLY_A=1\n")
    b = tmp_env("b.env", "FOO=bar\nONLY_B=2\n")
    rc = main([str(a), str(b), "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "missing_in_second" in data or "missing_in_first" in data
    assert rc == 0


def test_text_output_contains_labels(tmp_env, capsys):
    a = tmp_env("a.env", "KEY=val\n")
    b = tmp_env("b.env", "KEY=other\n")
    main([str(a), str(b), "--format", "text"])
    out = capsys.readouterr().out
    assert "KEY" in out


def test_no_differences_no_exit_code_flag(tmp_env):
    a = tmp_env("a.env", "X=1\n")
    b = tmp_env("b.env", "X=1\n")
    assert main([str(a), str(b), "--exit-code"]) == 0
