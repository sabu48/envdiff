"""Tests for envdiff.interpolator."""
from __future__ import annotations

import pytest

from envdiff.interpolator import InterpolateResult, _refs_in, interpolate


# ---------------------------------------------------------------------------
# _refs_in helpers
# ---------------------------------------------------------------------------

def test_refs_in_brace_style():
    assert _refs_in("${FOO}/bar") == ["FOO"]


def test_refs_in_bare_style():
    assert _refs_in("$HOST:$PORT") == ["HOST", "PORT"]


def test_refs_in_mixed():
    refs = _refs_in("${PROTO}://$HOST")
    assert "PROTO" in refs
    assert "HOST" in refs


def test_refs_in_empty_value():
    assert _refs_in("") == []
    assert _refs_in(None) == []


# ---------------------------------------------------------------------------
# interpolate — clean envs
# ---------------------------------------------------------------------------

def test_no_refs_unchanged():
    env = {"HOST": "localhost", "PORT": "5432"}
    result = interpolate(env)
    assert result.resolved["HOST"] == "localhost"
    assert result.resolved["PORT"] == "5432"
    assert result.is_clean()


def test_brace_ref_resolved():
    env = {"BASE": "http://localhost", "URL": "${BASE}/api"}
    result = interpolate(env)
    assert result.resolved["URL"] == "http://localhost/api"
    assert result.is_clean()


def test_bare_ref_resolved():
    env = {"HOST": "db", "DSN": "postgres://$HOST/mydb"}
    result = interpolate(env)
    assert result.resolved["DSN"] == "postgres://db/mydb"
    assert result.is_clean()


def test_chained_refs_resolved():
    env = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
    result = interpolate(env)
    assert result.resolved["C"] == "hello_world!"
    assert result.is_clean()


def test_none_value_stays_none():
    env = {"KEY": None}
    result = interpolate(env)
    assert result.resolved["KEY"] is None


# ---------------------------------------------------------------------------
# interpolate — unresolved references
# ---------------------------------------------------------------------------

def test_missing_ref_left_in_place():
    env = {"URL": "${MISSING}/path"}
    result = interpolate(env)
    assert "${MISSING}" in result.resolved["URL"]
    assert "URL" in result.unresolved_refs


def test_summary_reports_unresolved():
    env = {"X": "$GHOST"}
    result = interpolate(env)
    assert "unresolved refs" in result.summary()


# ---------------------------------------------------------------------------
# interpolate — cycle detection
# ---------------------------------------------------------------------------

def test_cycle_does_not_hang():
    env = {"A": "${B}", "B": "${A}"}
    result = interpolate(env)  # must terminate
    assert len(result.cycles) > 0


def test_summary_reports_cycles():
    env = {"A": "${A}"}
    result = interpolate(env)
    # self-reference is a cycle
    assert "cycles" in result.summary() or not result.is_clean()


# ---------------------------------------------------------------------------
# InterpolateResult.summary
# ---------------------------------------------------------------------------

def test_summary_clean():
    env = {"K": "v"}
    result = interpolate(env)
    assert result.summary() == "all references resolved"
