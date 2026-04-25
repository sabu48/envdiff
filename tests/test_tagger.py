"""Tests for envdiff.tagger."""
from __future__ import annotations

import pytest

from envdiff.tagger import TagMap, TagResult, build_tag_map, tag


@pytest.fixture()
def env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "SECRET_KEY": "s3cr3t",
        "DEBUG": "true",
        "PORT": "8080",
        "API_TOKEN": "tok_abc",
    }


@pytest.fixture()
def tag_map():
    return build_tag_map({
        "database": ["DATABASE_URL"],
        "security": ["SECRET_KEY", "API_TOKEN"],
        "runtime": ["DEBUG", "PORT"],
    })


@pytest.fixture()
def result(env, tag_map):
    return tag(env, tag_map)


def test_tag_result_is_tag_result(result):
    assert isinstance(result, TagResult)


def test_tagged_database_returns_correct_key(result):
    db = result.tagged("database")
    assert list(db.keys()) == ["DATABASE_URL"]


def test_tagged_security_returns_two_keys(result):
    sec = result.tagged("security")
    assert set(sec.keys()) == {"SECRET_KEY", "API_TOKEN"}


def test_tagged_unknown_tag_returns_empty(result):
    assert result.tagged("nonexistent") == {}


def test_untagged_returns_empty_when_all_tagged(result):
    # All five keys are tagged in our fixture
    assert result.untagged() == {}


def test_untagged_returns_keys_with_no_tag(env, tag_map):
    env_extra = dict(env)
    env_extra["UNTAGGED_KEY"] = "value"
    r = tag(env_extra, tag_map)
    untagged = r.untagged()
    assert "UNTAGGED_KEY" in untagged
    assert "DATABASE_URL" not in untagged


def test_tags_for_key(tag_map):
    assert "security" in tag_map.tags_for("SECRET_KEY")


def test_tags_for_untagged_key_empty(tag_map):
    assert tag_map.tags_for("UNKNOWN") == frozenset()


def test_all_tags_sorted(tag_map):
    assert tag_map.all_tags() == ["database", "runtime", "security"]


def test_add_merges_keys():
    tm = TagMap()
    tm.add("infra", ["HOST"])
    tm.add("infra", ["PORT"])
    assert {"HOST", "PORT"} == tm.keys_for("infra")


def test_env_unchanged_in_result(env, result):
    assert result.env == env
