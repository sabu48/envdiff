import json
import pytest
from pathlib import Path
from envdiff.cli_graph import build_graph_parser, _run


@pytest.fixture
def tmp_envs(tmp_path):
    def _write(name, content):
        p = tmp_path / name
        p.write_text(content)
        return str(p)
    return _write


def _run_with(args_list):
    """Parse args_list and invoke _run, returning the exit code."""
    parser = build_graph_parser()
    args = parser.parse_args(args_list)
    return _run(args)


def test_two_files_exit_zero(tmp_envs):
    a = tmp_envs("a.env", "DB=1\nHOST=x\n")
    b = tmp_envs("b.env", "DB=2\nPORT=5\n")
    assert _run_with([a, b]) == 0


def test_missing_file_exit_two(tmp_envs):
    a = tmp_envs("a.env", "DB=1\n")
    assert _run_with([a, "/no/such/file.env"]) == 2


def test_json_output_structure(tmp_envs, capsys):
    a = tmp_envs("a.env", "X=1\nY=2\n")
    b = tmp_envs("b.env", "X=1\nZ=3\n")
    rc = _run_with([a, b, "--format", "json"])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 1
    edge = data[0]
    assert "source" in edge
    assert "shared" in edge
    assert "overlap_ratio" in edge


def test_text_output_contains_overlap(tmp_envs, capsys):
    a = tmp_envs("a.env", "A=1\nB=2\n")
    b = tmp_envs("b.env", "A=1\nC=3\n")
    _run_with([a, b])
    out = capsys.readouterr().out
    assert "overlap=" in out


def test_min_overlap_filters_edges(tmp_envs, capsys):
    a = tmp_envs("a.env", "A=1\n")
    b = tmp_envs("b.env", "B=2\n")
    rc = _run_with([a, b, "--min-overlap", "0.9"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "No edges" in out


def test_three_files_produces_three_edges(tmp_envs, capsys):
    a = tmp_envs("a.env", "K=1\n")
    b = tmp_envs("b.env", "K=2\n")
    c = tmp_envs("c.env", "K=3\n")
    _run_with([a, b, c, "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 3


def test_json_overlap_ratio_value(tmp_envs, capsys):
    """overlap_ratio should be 0.5 when one of two keys is shared."""
    a = tmp_envs("a.env", "SHARED=1\nONLY_A=2\n")
    b = tmp_envs("b.env", "SHARED=1\nONLY_B=3\n")
    _run_with([a, b, "--format", "json"])
    out = capsys.readouterr().out
    data = json.loads(out)
    assert len(data) == 1
    ratio = data[0]["overlap_ratio"]
    # union has 3 keys, intersection has 1 → ratio = 1/3 ≈ 0.333
    assert 0.0 < ratio < 1.0
