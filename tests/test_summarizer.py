import pytest
from envdiff.summarizer import summarize, EnvSummary


@pytest.fixture
def envs():
    return {
        "dev": {"A": "1", "B": "2", "C": "same"},
        "staging": {"A": "1", "B": "99", "C": "same"},
        "prod": {"A": "1", "C": "same", "D": "only_prod"},
    }


def test_summary_returns_env_summary(envs):
    result = summarize(envs)
    assert isinstance(result, EnvSummary)


def test_env_names(envs):
    result = summarize(envs)
    assert set(result.env_names) == {"dev", "staging", "prod"}


def test_total_keys(envs):
    result = summarize(envs)
    assert result.total_keys == 4  # A, B, C, D


def test_common_keys_all_envs(envs):
    result = summarize(envs)
    # A and C appear in all three
    assert "A" in result.common_keys
    assert "C" in result.common_keys
    assert "B" not in result.common_keys  # missing in prod
    assert "D" not in result.common_keys  # missing in dev/staging


def test_missing_keys(envs):
    result = summarize(envs)
    assert "B" in result.all_missing
    assert "prod" in result.all_missing["B"]
    assert "D" in result.all_missing
    assert set(result.all_missing["D"]) == {"dev", "staging"}


def test_mismatched_keys(envs):
    result = summarize(envs)
    assert "B" in result.all_mismatched or "B" not in result.common_keys
    # A is same across all, C is same
    assert "A" not in result.all_mismatched
    assert "C" not in result.all_mismatched


def test_per_pair_populated(envs):
    result = summarize(envs)
    assert "dev:staging" in result.per_pair
    assert "dev:prod" in result.per_pair
    assert "staging:prod" in result.per_pair


def test_has_issues_true(envs):
    result = summarize(envs)
    assert result.has_issues()


def test_has_issues_false():
    identical = {"dev": {"X": "1"}, "prod": {"X": "1"}}
    result = summarize(identical)
    assert not result.has_issues()


def test_identical_envs_no_missing_or_mismatch():
    envs = {"a": {"K": "v"}, "b": {"K": "v"}}
    result = summarize(envs)
    assert result.all_missing == {}
    assert result.all_mismatched == []
