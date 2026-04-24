"""Tests for envdiff.auditor."""
import time
import json
import pytest
from pathlib import Path
from envdiff.auditor import (
    AuditEntry, AuditLog, record, save_audit_log, load_audit_log
)


@pytest.fixture
def log() -> AuditLog:
    return AuditLog()


def test_record_appends_entry(log):
    entry = record(log, "diff", ["a.env", "b.env"], "ok")
    assert len(log) == 1
    assert isinstance(entry, AuditEntry)


def test_record_stores_operation(log):
    record(log, "lint", ["a.env"], "ok")
    assert log.entries[0].operation == "lint"


def test_record_stores_outcome(log):
    record(log, "diff", ["a.env", "b.env"], "differences", detail="KEY_A missing")
    assert log.entries[0].outcome == "differences"
    assert log.entries[0].detail == "KEY_A missing"


def test_record_timestamp_is_recent(log):
    before = time.time()
    record(log, "diff", [], "ok")
    after = time.time()
    assert before <= log.entries[0].timestamp <= after


def test_since_filters_by_cutoff(log):
    record(log, "diff", [], "ok")
    cutoff = time.time()
    record(log, "lint", [], "ok")
    filtered = log.since(cutoff)
    assert len(filtered) == 1
    assert filtered.entries[0].operation == "lint"


def test_by_operation_filters(log):
    record(log, "diff", [], "ok")
    record(log, "lint", [], "ok")
    record(log, "diff", [], "differences")
    diff_log = log.by_operation("diff")
    assert len(diff_log) == 2
    assert all(e.operation == "diff" for e in diff_log.entries)


def test_save_and_load_roundtrip(tmp_path, log):
    record(log, "merge", ["a.env", "b.env"], "ok")
    path = tmp_path / "audit.json"
    save_audit_log(log, path)
    loaded = load_audit_log(path)
    assert len(loaded) == 1
    assert loaded.entries[0].operation == "merge"
    assert loaded.entries[0].outcome == "ok"


def test_save_creates_valid_json(tmp_path, log):
    record(log, "diff", ["x.env"], "ok", detail="clean")
    path = tmp_path / "audit.json"
    save_audit_log(log, path)
    data = json.loads(path.read_text())
    assert isinstance(data, list)
    assert data[0]["operation"] == "diff"


def test_load_preserves_detail(tmp_path, log):
    record(log, "validate", ["prod.env"], "error", detail="KEY_SECRET missing")
    path = tmp_path / "audit.json"
    save_audit_log(log, path)
    loaded = load_audit_log(path)
    assert loaded.entries[0].detail == "KEY_SECRET missing"


def test_empty_log_saves_empty_list(tmp_path, log):
    path = tmp_path / "audit.json"
    save_audit_log(log, path)
    data = json.loads(path.read_text())
    assert data == []
