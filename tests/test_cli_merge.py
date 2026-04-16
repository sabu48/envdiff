"""Integration tests for cli_merge."""
import json
import pytest
from pathlib import Path
from unittest.mock import patch
from envdiff.cli_merge import build_merge_parser, _run_merge


@pytest.fixture()
def tmp_env(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def _run(args_list):
    parser = build_merge_parser()
    args = parser.parse_args(args_list)
    return _run_merge(args)


def test_merge_two_files_exit_zero(tmp_env):
    a = tmp_env("a.env", "X=1\nY=2\n")
    b = tmp_env("b.env", "Z=3\n")
    assert _run([a, b]) == 0


def test_merge_conflict_no_flag_exit_zero(tmp_env):
    a = tmp_env("a.env", "HOST=local\n")
    b = tmp_env("b.env", "HOST=prod\n")
    assert _run([a, b]) == 0


def test_merge_conflict_with_flag_exit_one(tmp_env):
    a = tmp_env("a.env", "HOST=local\n")
    b = tmp_env("b.env", "HOST=prod\n")
    assert _run([a, b, "--fail-on-conflicts"]) == 1


def test_merge_missing_file_exit_two(tmp_env):
    a = tmp_env("a.env", "X=1\n")
    assert _run([a, "/nonexistent/.env"]) == 2


def test_merge_json_output(tmp_env, capsys):
    a = tmp_env("a.env", "X=1\n")
    b = tmp_env("b.env", "Y=2\n")
    _run([a, b, "--format", "json"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["X"] == "1"
    assert data["Y"] == "2"


def test_merge_writes_output_file(tmp_env, tmp_path):
    a = tmp_env("a.env", "X=1\n")
    out = str(tmp_path / "merged.env")
    _run([a, "--output", out])
    assert Path(out).exists()
    assert "X=1" in Path(out).read_text()


def test_first_strategy_keeps_first(tmp_env, capsys):
    a = tmp_env("a.env", "HOST=first\n")
    b = tmp_env("b.env", "HOST=second\n")
    _run([a, b, "--strategy", "first"])
    captured = capsys.readouterr()
    assert "HOST=first" in captured.out
