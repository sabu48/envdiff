"""Tests for envdiff.snapshot_reporter."""

import json

import pytest

from envdiff.snapshot_reporter import (
    format_snapshot_json,
    format_snapshot_text,
    render_snapshot_diff,
)


@pytest.fixture()
def diff():
    return {
        "staging": {
            "added": {"NEW_KEY": "hello"},
            "removed": {"OLD_KEY": "bye"},
            "changed": {"DB_URL": {"old": "postgres://old", "new": "postgres://new"}},
        }
    }


def test_text_no_changes_message():
    assert "No changes" in format_snapshot_text({})


def test_text_shows_env_name(diff):
    out = format_snapshot_text(diff)
    assert "staging" in out


def test_text_shows_added_section(diff):
    out = format_snapshot_text(diff)
    assert "ADDED" in out
    assert "NEW_KEY" in out


def test_text_shows_removed_section(diff):
    out = format_snapshot_text(diff)
    assert "REMOVED" in out
    assert "OLD_KEY" in out


def test_text_shows_changed_section(diff):
    out = format_snapshot_text(diff)
    assert "CHANGED" in out
    assert "DB_URL" in out
    assert "->" in out


def test_json_is_valid(diff):
    out = format_snapshot_json(diff)
    parsed = json.loads(out)
    assert "staging" in parsed


def test_json_contains_added(diff):
    out = format_snapshot_json(diff)
    parsed = json.loads(out)
    assert parsed["staging"]["added"]["NEW_KEY"] == "hello"


def test_render_defaults_to_text(diff):
    out = render_snapshot_diff(diff)
    assert "staging" in out
    assert "[" in out


def test_render_json_format(diff):
    out = render_snapshot_diff(diff, fmt="json")
    parsed = json.loads(out)
    assert "staging" in parsed
