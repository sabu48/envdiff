"""Patch an .env file by applying a diff result: add missing keys, update mismatched values."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class PatchResult:
    patched: Dict[str, Optional[str]]
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    skipped: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.added or self.updated)

    def summary(self) -> str:
        parts = []
        if self.added:
            parts.append(f"added: {', '.join(sorted(self.added))}")
        if self.updated:
            parts.append(f"updated: {', '.join(sorted(self.updated))}")
        if self.skipped:
            parts.append(f"skipped: {', '.join(sorted(self.skipped))}")
        return "; ".join(parts) if parts else "no changes"


def patch(
    base: Dict[str, Optional[str]],
    diff: DiffResult,
    *,
    add_missing: bool = True,
    update_mismatched: bool = True,
    skip_keys: Optional[List[str]] = None,
) -> PatchResult:
    """Return a new env dict with missing/mismatched keys applied from diff."""
    skip = set(skip_keys or [])
    patched = dict(base)
    added: List[str] = []
    updated: List[str] = []
    skipped: List[str] = []

    if add_missing:
        for key, value in diff.missing_in_first.items():
            if key in skip:
                skipped.append(key)
                continue
            patched[key] = value
            added.append(key)

    if update_mismatched:
        for key, (_, new_val) in diff.mismatched.items():
            if key in skip:
                skipped.append(key)
                continue
            patched[key] = new_val
            updated.append(key)

    return PatchResult(patched=patched, added=added, updated=updated, skipped=skipped)


def write_patch(path: Path, patched: Dict[str, Optional[str]]) -> None:
    """Write a patched env dict to a file in KEY=VALUE format."""
    lines = []
    for key, value in patched.items():
        if value is None:
            lines.append(f"{key}=")
        else:
            needs_quotes = " " in value or "#" in value
            lines.append(f"{key}=\"{value}\"" if needs_quotes else f"{key}={value}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
