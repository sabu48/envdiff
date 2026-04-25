"""Tests for envdiff.pin_reporter."""
import json

import pytest

from envdiff.pinner import PinResult
from envdiff.pin_reporter import format_pin_json, format_pin_text, render_pin


@pytest.fixture()
def clean_result():
    return PinResult(pinned={"A": "1"}, deviations={}, new_keys=[], removed_keys=[])


@pytest.fixture()
def dirty_result():
    return PinResult(
        pinned={"A": "1", "B": "old"},
        deviations={"B": ("old", "new")},
        new_keys=["C"],
        removed_keys=["D"],
    )


def test_text_no_deviations(clean_result):
    out = format_pin_text(clean_result)
    assert "No deviations" in out


def test_text_shows_deviated_key(dirty_result):
    out = format_pin_text(dirty_result)
    assert "B" in out
    assert "old" in out
    assert "new" in out


def test_text_shows_new_keys(dirty_result):
    out = format_pin_text(dirty_result)
    assert "C" in out
    assert "New keys" in out


def test_text_shows_removed_keys(dirty_result):
    out = format_pin_text(dirty_result)
    assert "D" in out
    assert "Removed keys" in out


def test_json_has_deviations_flag(dirty_result):
    data = json.loads(format_pin_json(dirty_result))
    assert data["has_deviations"] is True


def test_json_clean_has_no_deviations(clean_result):
    data = json.loads(format_pin_json(clean_result))
    assert data["has_deviations"] is False
    assert data["deviations"] == {}


def test_json_deviation_structure(dirty_result):
    data = json.loads(format_pin_json(dirty_result))
    assert data["deviations"]["B"]["pinned"] == "old"
    assert data["deviations"]["B"]["current"] == "new"


def test_render_delegates_format(dirty_result):
    text_out = render_pin(dirty_result, fmt="text")
    json_out = render_pin(dirty_result, fmt="json")
    assert "Deviated" in text_out
    assert json.loads(json_out)["has_deviations"] is True
