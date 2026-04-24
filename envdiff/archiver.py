"""Archive and restore .env snapshots to/from a zip archive."""

from __future__ import annotations

import io
import json
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

META_FILENAME = "_archive_meta.json"


@dataclass
class ArchiveMeta:
    created_at: str
    labels: List[str]
    file_count: int


@dataclass
class ArchiveResult:
    meta: ArchiveMeta
    envs: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)

    @property
    def env_names(self) -> List[str]:
        return list(self.envs.keys())

    def get(self, label: str) -> Optional[Dict[str, Optional[str]]]:
        return self.envs.get(label)


def create_archive(
    files: List[Path],
    labels: Optional[List[str]] = None,
) -> bytes:
    """Serialize one or more parsed .env files into an in-memory zip archive."""
    from envdiff.parser import parse_env_file

    if labels is None:
        labels = [p.name for p in files]
    if len(labels) != len(files):
        raise ValueError("labels length must match files length")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        envs: Dict[str, Dict[str, Optional[str]]] = {}
        for label, path in zip(labels, files):
            parsed = parse_env_file(path)
            envs[label] = parsed
            zf.writestr(f"{label}.json", json.dumps(parsed))

        meta = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "labels": labels,
            "file_count": len(files),
        }
        zf.writestr(META_FILENAME, json.dumps(meta))

    return buf.getvalue()


def save_archive(files: List[Path], dest: Path, labels: Optional[List[str]] = None) -> None:
    """Write a zip archive of .env files to *dest*."""
    dest.write_bytes(create_archive(files, labels))


def load_archive(src: Path) -> ArchiveResult:
    """Load an archive produced by :func:`save_archive`."""
    with zipfile.ZipFile(src, mode="r") as zf:
        raw_meta = json.loads(zf.read(META_FILENAME))
        meta = ArchiveMeta(
            created_at=raw_meta["created_at"],
            labels=raw_meta["labels"],
            file_count=raw_meta["file_count"],
        )
        envs: Dict[str, Dict[str, Optional[str]]] = {}
        for label in meta.labels:
            raw = json.loads(zf.read(f"{label}.json"))
            envs[label] = {k: (v if v is not None else None) for k, v in raw.items()}

    return ArchiveResult(meta=meta, envs=envs)
