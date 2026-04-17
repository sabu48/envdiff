"""Tests for envdiff.renamer."""
import pytest
from envdiff.comparator import DiffResult
from envdiff.renamer import RenameMap, load_rename_map, apply_rename


@pytest.fixture
def diff():
    return DiffResult(
        missing_in_second={"OLD_DB_HOST"},
        missing_in_first={"OLD_API_KEY"},
        mismatched={"OLD_PORT": ("3000", "4000")},
        identical={"OLD_DEBUG"},
    )


@pytest.fixture
def rename_map():
    rm = RenameMap()
    rm.add("OLD_DB_HOST", "DB_HOST")
    rm.add("OLD_API_KEY", "API_KEY")
    rm.add("OLD_PORT", "PORT")
    rm.add("OLD_DEBUG", "DEBUG")
    return rm


def test_rename_map_apply_known(rename_map):
    assert rename_map.apply("OLD_DB_HOST") == "DB_HOST"


def test_rename_map_apply_unknown(rename_map):
    assert rename_map.apply("UNKNOWN_KEY") == "UNKNOWN_KEY"


def test_apply_rename_missing_in_second(diff, rename_map):
    result = apply_rename(diff, rename_map)
    assert "DB_HOST" in result.missing_in_second
    assert "OLD_DB_HOST" not in result.missing_in_second


def test_apply_rename_missing_in_first(diff, rename_map):
    result = apply_rename(diff, rename_map)
    assert "API_KEY" in result.missing_in_first


def test_apply_rename_mismatched(diff, rename_map):
    result = apply_rename(diff, rename_map)
    assert "PORT" in result.mismatched
    assert result.mismatched["PORT"] == ("3000", "4000")


def test_apply_rename_identical(diff, rename_map):
    result = apply_rename(diff, rename_map)
    assert "DEBUG" in result.identical


def test_load_rename_map(tmp_path):
    f = tmp_path / "renames.env"
    f.write_text("# comment\nOLD_KEY=NEW_KEY\nFOO=BAR\n")
    rm = load_rename_map(str(f))
    assert rm.apply("OLD_KEY") == "NEW_KEY"
    assert rm.apply("FOO") == "BAR"
    assert rm.apply("MISSING") == "MISSING"


def test_load_rename_map_skips_blank_and_comments(tmp_path):
    f = tmp_path / "renames.env"
    f.write_text("\n# skip\nA=B\n")
    rm = load_rename_map(str(f))
    assert len(rm.mappings) == 1
