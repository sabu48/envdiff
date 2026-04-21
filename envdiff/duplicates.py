"""Detect duplicate keys within a single .env file."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class DuplicateResult:
    path: str
    duplicates: Dict[str, List[int]]  # key -> list of line numbers

    @property
    def has_duplicates(self) -> bool:
        return bool(self.duplicates)

    def summary(self) -> str:
        if not self.has_duplicates:
            return f"{self.path}: no duplicate keys found."
        lines = [f"{self.path}: {len(self.duplicates)} duplicate key(s) found."]
        for key, linenos in sorted(self.duplicates.items()):
            nums = ", ".join(str(n) for n in linenos)
            lines.append(f"  {key}: lines {nums}")
        return "\n".join(lines)


def find_duplicates(path: str | Path) -> DuplicateResult:
    """Parse *path* and return any keys that appear more than once.

    Only non-blank, non-comment lines that contain '=' are considered.
    Line numbers in the result are 1-based.
    """
    path = Path(path)
    seen: Dict[str, List[int]] = {}

    with path.open(encoding="utf-8") as fh:
        for lineno, raw in enumerate(fh, start=1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key = line.split("=", 1)[0].strip()
            # Strip optional 'export ' prefix
            if key.lower().startswith("export "):
                key = key[7:].strip()
            if not key:
                continue
            seen.setdefault(key, []).append(lineno)

    duplicates = {k: v for k, v in seen.items() if len(v) > 1}
    return DuplicateResult(path=str(path), duplicates=duplicates)


def find_duplicates_many(
    paths: List[str | Path],
) -> Dict[str, DuplicateResult]:
    """Run :func:`find_duplicates` across multiple files.

    Returns a mapping of path string -> DuplicateResult.
    """
    return {str(p): find_duplicates(p) for p in paths}
