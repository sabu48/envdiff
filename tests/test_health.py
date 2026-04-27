"""Tests for envdiff.health."""
import os
import textwrap

import pytest

from envdiff.health import HealthReport, check


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


def _write(p, content: str):
    p.write_text(textwrap.dedent(content))
    return str(p)


# ---------------------------------------------------------------------------
# HealthReport unit tests
# ---------------------------------------------------------------------------

def test_health_report_defaults():
    r = HealthReport(path=".env")
    assert r.score == 100
    assert r.healthy is True
    assert r.lint_issues == []
    assert r.empty_keys == []
    assert r.secret_hits == []


def test_health_report_unhealthy_below_80():
    r = HealthReport(path=".env", score=79)
    assert r.healthy is False


def test_health_report_summary_contains_score():
    r = HealthReport(path=".env", score=95)
    assert "95/100" in r.summary()


def test_health_report_summary_ok_status():
    r = HealthReport(path=".env", score=100)
    assert "OK" in r.summary()


def test_health_report_summary_unhealthy_status():
    r = HealthReport(path=".env", score=50)
    assert "UNHEALTHY" in r.summary()


# ---------------------------------------------------------------------------
# check() integration tests
# ---------------------------------------------------------------------------

def test_check_clean_file_scores_100(tmp):
    path = _write(tmp / ".env", """\
        DB_HOST=localhost
        DB_PORT=5432
    """)
    env = {"DB_HOST": "localhost", "DB_PORT": "5432"}
    result = check(path, env)
    assert result.score == 100
    assert result.healthy is True


def test_check_empty_key_reduces_score(tmp):
    path = _write(tmp / ".env", """\
        DB_HOST=localhost
        API_KEY=
    """)
    env = {"DB_HOST": "localhost", "API_KEY": ""}
    result = check(path, env)
    assert result.score < 100
    assert "API_KEY" in result.empty_keys


def test_check_secret_hit_reduces_score(tmp):
    path = _write(tmp / ".env", """\
        DB_PASSWORD=supersecret123
    """)
    env = {"DB_PASSWORD": "supersecret123"}
    result = check(path, env)
    assert result.score < 100
    assert "DB_PASSWORD" in result.secret_hits


def test_check_without_env_skips_profiler_and_scanner(tmp):
    path = _write(tmp / ".env", """\
        DB_HOST=localhost
    """)
    result = check(path)  # no env kwarg
    assert result.empty_keys == []
    assert result.secret_hits == []


def test_check_score_never_below_zero(tmp):
    path = _write(tmp / ".env", """\
        password=abc
        token=xyz
        api_key=123
        secret=oops
    """)
    env = {
        "password": "abc",
        "token": "xyz",
        "api_key": "123",
        "secret": "oops",
    }
    result = check(path, env)
    assert result.score >= 0
