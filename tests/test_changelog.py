"""Tests for envdiff.changelog."""
from __future__ import annotations

import pytest

from envdiff.changelog import ChangelogEntry, ChangelogReport, build_changelog
from envdiff.snapshotter import Snapshot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_snapshot(envs: dict) -> Snapshot:
    """Build a minimal Snapshot from a plain dict of {label: {key: value}}."""
    return Snapshot(envs=envs, created_at="2024-01-01T00:00:00")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def before():
    return _make_snapshot({
        "production": {"DB_HOST": "prod-db", "DEBUG": "false", "OLD_KEY": "gone"},
        "staging": {"DB_HOST": "stage-db", "DEBUG": "true"},
    })


@pytest.fixture()
def after():
    return _make_snapshot({
        "production": {"DB_HOST": "prod-db-v2", "DEBUG": "false", "NEW_KEY": "hello"},
        "staging": {"DB_HOST": "stage-db", "DEBUG": "true"},
    })


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_build_changelog_returns_report(before, after):
    report = build_changelog(before, after)
    assert isinstance(report, ChangelogReport)


def test_identical_envs_no_changes():
    snap = _make_snapshot({"prod": {"KEY": "val"}})
    report = build_changelog(snap, snap)
    assert not report.has_changes


def test_has_changes_when_key_added(before, after):
    report = build_changelog(before, after)
    assert report.has_changes


def test_added_key_detected(before, after):
    report = build_changelog(before, after)
    prod = next(e for e in report.entries if e.env_name == "production")
    assert "NEW_KEY" in prod.added
    assert prod.added["NEW_KEY"] == "hello"


def test_removed_key_detected(before, after):
    report = build_changelog(before, after)
    prod = next(e for e in report.entries if e.env_name == "production")
    assert "OLD_KEY" in prod.removed


def test_changed_value_detected(before, after):
    report = build_changelog(before, after)
    prod = next(e for e in report.entries if e.env_name == "production")
    assert "DB_HOST" in prod.changed
    assert prod.changed["DB_HOST"] == ("prod-db", "prod-db-v2")


def test_unchanged_env_has_no_changes(before, after):
    report = build_changelog(before, after)
    staging = next(e for e in report.entries if e.env_name == "staging")
    assert not staging.has_changes


def test_summary_contains_env_name(before, after):
    report = build_changelog(before, after)
    s = report.summary()
    assert "[production]" in s


def test_summary_no_changes_message():
    snap = _make_snapshot({"prod": {"A": "1"}})
    report = build_changelog(snap, snap)
    assert "No changes" in report.summary()


def test_entries_sorted_by_env_name():
    before = _make_snapshot({"z_env": {"K": "1"}, "a_env": {"K": "1"}})
    after = _make_snapshot({"z_env": {"K": "2"}, "a_env": {"K": "2"}})
    report = build_changelog(before, after)
    names = [e.env_name for e in report.entries]
    assert names == sorted(names)
