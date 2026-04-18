"""Tests for envdiff.cli_watch."""
import os
import time
import threading
from pathlib import Path

import pytest

from envdiff.cli_watch import build_watch_parser, _run_watch


@pytest.fixture()
def tmp_env(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def _run(args_list, tmp_path):
    parser = build_watch_parser()
    args = parser.parse_args(args_list)
    return _run_watch(args)


def test_watch_exits_zero_no_changes(tmp_env):
    p = tmp_env / "a.env"
    _write(p, "FOO=bar\n")
    code = _run([str(p), "--max-cycles", "2", "--interval", "0.01"], tmp_env)
    assert code == 0


def test_watch_detects_and_prints_change(tmp_env, capsys):
    p = tmp_env / "a.env"
    _write(p, "FOO=bar\n")

    def _modify():
        time.sleep(0.05)
        _write(p, "FOO=changed\n")
        future = time.time() + 2
        os.utime(str(p), (future, future))

    t = threading.Thread(target=_modify)
    t.start()
    _run([str(p), "--max-cycles", "15", "--interval", "0.02"], tmp_env)
    t.join()

    captured = capsys.readouterr()
    assert "change detected" in captured.out


def test_watch_json_format_flag_accepted(tmp_env):
    p = tmp_env / "a.env"
    _write(p, "A=1\n")
    code = _run([str(p), "--format", "json", "--max-cycles", "1", "--interval", "0.01"], tmp_env)
    assert code == 0


def test_build_watch_parser_defaults(tmp_env):
    p = tmp_env / "x.env"
    _write(p, "")
    parser = build_watch_parser()
    args = parser.parse_args([str(p)])
    assert args.interval == 1.0
    assert args.fmt == "text"
    assert args.max_cycles is None
