"""Tests for envdiff.reporter."""

import json

import pytest

from envdiff.comparator import DiffResult
from envdiff.reporter import render, format_text, format_json


@pytest.fixture
def clean_result():
    return DiffResult(set(), set(), {})


@pytest.fixture
def dirty_result():
    return DiffResult(
        missing_in_second={"SECRET"},
        missing_in_first={"NEW_KEY"},
        mismatched_values={"DB_HOST": ("localhost", "prod.db.internal")},
    )


def test_text_no_differences(clean_result):
    output = format_text(clean_result, "dev.env", "prod.env")
    assert "No differences" in output
    assert "dev.env" in output
    assert "prod.env" in output


def test_text_missing_in_second(dirty_result):
    output = format_text(dirty_result, "dev.env", "prod.env")
    assert "Missing in prod.env" in output
    assert "SECRET" in output


def test_text_missing_in_first(dirty_result):
    output = format_text(dirty_result, "dev.env", "prod.env")
    assert "Missing in dev.env" in output
    assert "NEW_KEY" in output


def test_text_mismatched_values(dirty_result):
    output = format_text(dirty_result, "dev.env", "prod.env")
    assert "DB_HOST" in output
    assert "localhost" in output
    assert "prod.db.internal" in output


def test_text_includes_summary(dirty_result):
    output = format_text(dirty_result, "dev.env", "prod.env")
    assert dirty_result.summary() in output


def test_json_no_differences(clean_result):
    raw = format_json(clean_result, "a.env", "b.env")
    data = json.loads(raw)
    assert data["has_differences"] is False
    assert data["missing_in_second"] == []
    assert data["missing_in_first"] == []
    assert data["mismatched_values"] == {}


def test_json_dirty(dirty_result):
    raw = format_json(dirty_result, "a.env", "b.env")
    data = json.loads(raw)
    assert data["has_differences"] is True
    assert "SECRET" in data["missing_in_second"]
    assert "NEW_KEY" in data["missing_in_first"]
    assert data["mismatched_values"]["DB_HOST"] == {
        "a": "localhost", "b": "prod.db.internal"
    }


def test_render_defaults_to_text(clean_result):
    output = render(clean_result)
    assert "No differences" in output


def test_render_json_format(dirty_result):
    output = render(dirty_result, fmt="json")
    data = json.loads(output)
    assert "has_differences" in data
