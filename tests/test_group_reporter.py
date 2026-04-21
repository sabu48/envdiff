"""Tests for envdiff.group_reporter."""
import json

import pytest

from envdiff.grouper import GroupReport
from envdiff.group_reporter import format_group_text, format_group_json, render_group


@pytest.fixture()
def report() -> GroupReport:
    return GroupReport(
        groups={
            "DB": ["DB_HOST", "DB_PORT"],
            "APP": ["APP_ENV"],
        },
        ungrouped=["SECRET"],
    )


@pytest.fixture()
def empty_report() -> GroupReport:
    return GroupReport(groups={}, ungrouped=[])


def test_text_contains_prefix_header(report):
    out = format_group_text(report)
    assert "=== DB ===" in out
    assert "=== APP ===" in out


def test_text_lists_keys(report):
    out = format_group_text(report)
    assert "DB_HOST" in out
    assert "DB_PORT" in out
    assert "APP_ENV" in out


def test_text_shows_ungrouped_section(report):
    out = format_group_text(report)
    assert "(ungrouped)" in out
    assert "SECRET" in out


def test_text_empty_report_message(empty_report):
    out = format_group_text(empty_report)
    assert "No differences" in out


def test_json_contains_groups_key(report):
    data = json.loads(format_group_json(report))
    assert "groups" in data
    assert "DB" in data["groups"]


def test_json_contains_ungrouped(report):
    data = json.loads(format_group_json(report))
    assert "ungrouped" in data
    assert "SECRET" in data["ungrouped"]


def test_render_defaults_to_text(report):
    out = render_group(report)
    assert "=== DB ===" in out


def test_render_json_format(report):
    out = render_group(report, fmt="json")
    data = json.loads(out)
    assert isinstance(data["groups"], dict)
