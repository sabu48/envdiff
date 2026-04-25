"""Tests for envdiff.tag_reporter."""
from __future__ import annotations

import json

import pytest

from envdiff.tagger import build_tag_map, tag
from envdiff.tag_reporter import format_tag_text, format_tag_json, render_tag


@pytest.fixture()
def result():
    env = {"DB_URL": "postgres://", "SECRET": "abc", "PORT": "5432"}
    tm = build_tag_map({"database": ["DB_URL"], "security": ["SECRET"]})
    return tag(env, tm)


def test_text_contains_tag_header(result):
    out = format_tag_text(result)
    assert "[database]" in out
    assert "[security]" in out


def test_text_contains_key_value(result):
    out = format_tag_text(result)
    assert "DB_URL=postgres://" in out


def test_text_untagged_section_present(result):
    out = format_tag_text(result)
    assert "[untagged]" in out
    assert "PORT=5432" in out


def test_text_no_keys_message():
    from envdiff.tagger import TagMap, TagResult
    r = TagResult(env={}, tag_map=TagMap())
    assert format_tag_text(r) == "No keys.\n"


def test_json_structure(result):
    out = json.loads(format_tag_json(result))
    assert "database" in out
    assert "security" in out
    assert out["database"]["DB_URL"] == "postgres://"


def test_json_untagged_key_present(result):
    out = json.loads(format_tag_json(result))
    assert "untagged" in out
    assert "PORT" in out["untagged"]


def test_render_text_default(result):
    assert "[database]" in render_tag(result)


def test_render_json(result):
    out = render_tag(result, fmt="json")
    parsed = json.loads(out)
    assert isinstance(parsed, dict)
