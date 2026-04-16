"""Tests for envdiff.parser module."""

import textwrap
from pathlib import Path

import pytest

from envdiff.parser import parse_env_file


@pytest.fixture()
def env_file(tmp_path: Path):
    """Factory fixture that writes content to a temp .env file."""

    def _write(content: str) -> Path:
        p = tmp_path / ".env"
        p.write_text(textwrap.dedent(content), encoding="utf-8")
        return p

    return _write


def test_basic_key_value(env_file):
    path = env_file("""
        DATABASE_URL=postgres://localhost/mydb
        DEBUG=true
    """)
    result = parse_env_file(path)
    assert result["DATABASE_URL"] == "postgres://localhost/mydb"
    assert result["DEBUG"] == "true"


def test_quoted_values(env_file):
    path = env_file("""
        SECRET_KEY="my secret value"
        APP_NAME='My App'
    """)
    result = parse_env_file(path)
    assert result["SECRET_KEY"] == "my secret value"
    assert result["APP_NAME"] == "My App"


def test_comments_and_blank_lines_skipped(env_file):
    path = env_file("""
        # This is a comment
        FOO=bar

        # Another comment
        BAZ=qux
    """)
    result = parse_env_file(path)
    assert list(result.keys()) == ["FOO", "BAZ"]


def test_empty_value(env_file):
    path = env_file("EMPTY_KEY=\n")
    result = parse_env_file(path)
    assert result["EMPTY_KEY"] == ""


def test_malformed_lines_ignored(env_file):
    path = env_file("""
        VALID=yes
        this is not valid
        =NOKEY
    """)
    result = parse_env_file(path)
    assert result == {"VALID": "yes"}


def test_file_not_found(tmp_path):
    with pytest.raises(FileNotFoundError):
        parse_env_file(tmp_path / "nonexistent.env")


def test_spaces_around_equals(env_file):
    path = env_file("KEY = value with spaces \n")
    result = parse_env_file(path)
    assert result["KEY"] == "value with spaces"
