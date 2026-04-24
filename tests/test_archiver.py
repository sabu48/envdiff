"""Tests for envdiff.archiver."""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from envdiff.archiver import (
    ArchiveMeta,
    ArchiveResult,
    create_archive,
    load_archive,
    save_archive,
)


@pytest.fixture()
def tmp(tmp_path: Path) -> Path:
    return tmp_path


def _write(path: Path, content: str) -> Path:
    path.write_text(content)
    return path


def test_create_archive_returns_bytes(tmp: Path) -> None:
    f = _write(tmp / ".env", "KEY=value\n")
    result = create_archive([f])
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_archive_contains_env_json(tmp: Path) -> None:
    f = _write(tmp / ".env", "FOO=bar\nBAZ=qux\n")
    data = create_archive([f], labels=["prod"])
    with zipfile.ZipFile(__import__("io").BytesIO(data)) as zf:
        names = zf.namelist()
    assert "prod.json" in names
    assert "_archive_meta.json" in names


def test_archive_env_json_content(tmp: Path) -> None:
    f = _write(tmp / ".env", "FOO=bar\n")
    data = create_archive([f], labels=["staging"])
    with zipfile.ZipFile(__import__("io").BytesIO(data)) as zf:
        payload = json.loads(zf.read("staging.json"))
    assert payload["FOO"] == "bar"


def test_save_and_load_roundtrip(tmp: Path) -> None:
    f1 = _write(tmp / "a.env", "ALPHA=1\nBETA=2\n")
    f2 = _write(tmp / "b.env", "ALPHA=1\nGAMMA=3\n")
    archive_path = tmp / "envs.zip"
    save_archive([f1, f2], archive_path, labels=["env_a", "env_b"])

    result = load_archive(archive_path)
    assert isinstance(result, ArchiveResult)
    assert set(result.env_names) == {"env_a", "env_b"}
    assert result.get("env_a") == {"ALPHA": "1", "BETA": "2"}
    assert result.get("env_b") == {"ALPHA": "1", "GAMMA": "3"}


def test_meta_file_count(tmp: Path) -> None:
    files = [_write(tmp / f"e{i}.env", f"K{i}=v{i}\n") for i in range(3)]
    archive_path = tmp / "multi.zip"
    save_archive(files, archive_path)
    result = load_archive(archive_path)
    assert result.meta.file_count == 3


def test_meta_labels_default_to_filename(tmp: Path) -> None:
    f = _write(tmp / "production.env", "X=1\n")
    data = create_archive([f])
    with zipfile.ZipFile(__import__("io").BytesIO(data)) as zf:
        meta = json.loads(zf.read("_archive_meta.json"))
    assert meta["labels"] == ["production.env"]


def test_labels_length_mismatch_raises(tmp: Path) -> None:
    f = _write(tmp / ".env", "A=1\n")
    with pytest.raises(ValueError, match="labels length"):
        create_archive([f], labels=["one", "two"])


def test_get_unknown_label_returns_none(tmp: Path) -> None:
    f = _write(tmp / ".env", "A=1\n")
    archive_path = tmp / "out.zip"
    save_archive([f], archive_path, labels=["dev"])
    result = load_archive(archive_path)
    assert result.get("nonexistent") is None


def test_created_at_is_iso_format(tmp: Path) -> None:
    from datetime import datetime
    f = _write(tmp / ".env", "A=1\n")
    archive_path = tmp / "ts.zip"
    save_archive([f], archive_path)
    result = load_archive(archive_path)
    dt = datetime.fromisoformat(result.meta.created_at)
    assert dt.tzinfo is not None
