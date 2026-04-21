"""Tests for envdiff.snapshotter."""

import json
import time
from pathlib import Path

import pytest

from envdiff.snapshotter import (
    Snapshot,
    diff_snapshots,
    load_snapshot,
    save_snapshot,
    take_snapshot,
)


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


def _write(p: Path, content: str) -> str:
    p.write_text(content)
    return str(p)


def test_take_snapshot_reads_all_files(tmp):
    a = _write(tmp / "a.env", "FOO=1\nBAR=2\n")
    b = _write(tmp / "b.env", "FOO=1\nBAZ=3\n")
    snap = take_snapshot([a, b])
    assert "a.env" in snap.env_names()
    assert "b.env" in snap.env_names()


def test_take_snapshot_custom_labels(tmp):
    a = _write(tmp / "a.env", "FOO=1\n")
    snap = take_snapshot([a], labels=["production"])
    assert "production" in snap.env_names()


def test_take_snapshot_created_at_recent(tmp):
    a = _write(tmp / "a.env", "FOO=1\n")
    before = time.time()
    snap = take_snapshot([a])
    after = time.time()
    assert before <= snap.created_at <= after


def test_save_and_load_roundtrip(tmp):
    a = _write(tmp / "a.env", "KEY=val\n")
    snap = take_snapshot([a], labels=["staging"])
    dest = str(tmp / "snap.json")
    save_snapshot(snap, dest)
    loaded = load_snapshot(dest)
    assert loaded.env_names() == snap.env_names()
    assert loaded.get("staging") == {"KEY": "val"}


def test_save_creates_valid_json(tmp):
    a = _write(tmp / "a.env", "X=1\n")
    snap = take_snapshot([a])
    dest = str(tmp / "out.json")
    save_snapshot(snap, dest)
    data = json.loads(Path(dest).read_text())
    assert "created_at" in data
    assert "envs" in data


def test_diff_snapshots_detects_added(tmp):
    old = Snapshot(created_at=0.0, envs={"app": {"A": "1"}})
    new = Snapshot(created_at=1.0, envs={"app": {"A": "1", "B": "2"}})
    result = diff_snapshots(old, new)
    assert result["app"]["added"] == {"B": "2"}


def test_diff_snapshots_detects_removed(tmp):
    old = Snapshot(created_at=0.0, envs={"app": {"A": "1", "B": "2"}})
    new = Snapshot(created_at=1.0, envs={"app": {"A": "1"}})
    result = diff_snapshots(old, new)
    assert result["app"]["removed"] == {"B": "2"}


def test_diff_snapshots_detects_changed(tmp):
    old = Snapshot(created_at=0.0, envs={"app": {"A": "old"}})
    new = Snapshot(created_at=1.0, envs={"app": {"A": "new"}})
    result = diff_snapshots(old, new)
    assert result["app"]["changed"]["A"] == {"old": "old", "new": "new"}


def test_diff_snapshots_identical_returns_empty():
    env = {"A": "1", "B": "2"}
    old = Snapshot(created_at=0.0, envs={"app": dict(env)})
    new = Snapshot(created_at=1.0, envs={"app": dict(env)})
    result = diff_snapshots(old, new)
    assert result == {}
