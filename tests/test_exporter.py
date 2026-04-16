"""Tests for envdiff.exporter."""
from __future__ import annotations

import csv
import io
import json

import pytest

from envdiff.comparator import DiffResult
from envdiff.exporter import export, export_csv, export_json, export_markdown


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        missing_in_second={"ALPHA"},
        missing_in_first={"BETA"},
        mismatched={"GAMMA": ("old", "new")},
    )


@pytest.fixture()
def clean_result() -> DiffResult:
    return DiffResult(missing_in_second=set(), missing_in_first=set(), mismatched={})


def test_export_json_structure(result: DiffResult) -> None:
    raw = export_json(result)
    data = json.loads(raw)
    assert data["missing_in_second"] == ["ALPHA"]
    assert data["missing_in_first"] == ["BETA"]
    assert data["mismatched"]["GAMMA"] == {"first": "old", "second": "new"}


def test_export_json_clean(clean_result: DiffResult) -> None:
    data = json.loads(export_json(clean_result))
    assert data["missing_in_second"] == []
    assert data["missing_in_first"] == []
    assert data["mismatched"] == {}


def test_export_csv_headers(result: DiffResult) -> None:
    raw = export_csv(result)
    reader = csv.DictReader(io.StringIO(raw))
    assert reader.fieldnames == ["key", "category", "value_first", "value_second"]


def test_export_csv_rows(result: DiffResult) -> None:
    raw = export_csv(result)
    rows = list(csv.DictReader(io.StringIO(raw)))
    categories = {r["key"]: r["category"] for r in rows}
    assert categories["ALPHA"] == "missing_in_second"
    assert categories["BETA"] == "missing_in_first"
    assert categories["GAMMA"] == "mismatched"


def test_export_markdown_contains_table(result: DiffResult) -> None:
    md = export_markdown(result)
    assert "| Key |" in md
    assert "`ALPHA`" in md
    assert "`BETA`" in md
    assert "`old`" in md
    assert "`new`" in md


def test_export_dispatch_json(result: DiffResult) -> None:
    out = export(result, "json")
    json.loads(out)  # should not raise


def test_export_dispatch_csv(result: DiffResult) -> None:
    out = export(result, "csv")
    assert "key,category" in out


def test_export_dispatch_markdown(result: DiffResult) -> None:
    out = export(result, "markdown")
    assert "---" in out


def test_export_unknown_format_raises(result: DiffResult) -> None:
    with pytest.raises(ValueError, match="Unknown export format"):
        export(result, "xml")  # type: ignore[arg-type]
