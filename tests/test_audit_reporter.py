"""Tests for envdiff.audit_reporter."""
import json
import pytest
from envdiff.auditor import AuditLog, record
from envdiff.audit_reporter import (
    format_audit_text, format_audit_json, render_audit
)


@pytest.fixture
def log() -> AuditLog:
    lg = AuditLog()
    record(lg, "diff", ["staging.env", "prod.env"], "differences", detail="KEY_X missing")
    record(lg, "lint", ["dev.env"], "ok")
    return lg


@pytest.fixture
def empty_log() -> AuditLog:
    return AuditLog()


def test_text_empty_log_message(empty_log):
    out = format_audit_text(empty_log)
    assert "No audit entries" in out


def test_text_contains_operation(log):
    out = format_audit_text(log)
    assert "DIFF" in out
    assert "LINT" in out


def test_text_contains_outcome(log):
    out = format_audit_text(log)
    assert "differences" in out
    assert "ok" in out


def test_text_contains_files(log):
    out = format_audit_text(log)
    assert "staging.env" in out
    assert "prod.env" in out


def test_text_contains_detail(log):
    out = format_audit_text(log)
    assert "KEY_X missing" in out


def test_text_no_detail_skipped(log):
    out = format_audit_text(log)
    # lint entry has no detail — should not show 'detail' line for it
    lines = [l for l in out.splitlines() if "detail" in l]
    assert len(lines) == 1  # only the diff entry


def test_json_returns_list(log):
    data = json.loads(format_audit_json(log))
    assert isinstance(data, list)
    assert len(data) == 2


def test_json_fields_present(log):
    data = json.loads(format_audit_json(log))
    entry = data[0]
    assert "timestamp" in entry
    assert "operation" in entry
    assert "files" in entry
    assert "outcome" in entry
    assert "detail" in entry


def test_json_timestamp_is_string(log):
    data = json.loads(format_audit_json(log))
    assert isinstance(data[0]["timestamp"], str)
    assert "T" in data[0]["timestamp"]


def test_render_defaults_to_text(log):
    out = render_audit(log)
    assert "Audit Log" in out


def test_render_json_format(log):
    out = render_audit(log, fmt="json")
    data = json.loads(out)
    assert len(data) == 2
