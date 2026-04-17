"""Annotate a parsed env dict with metadata from a DiffResult."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional

from envdiff.comparator import DiffResult


@dataclass
class AnnotatedKey:
    key: str
    value: Optional[str]
    status: str  # 'ok' | 'missing_in_first' | 'missing_in_second' | 'mismatch'
    other_value: Optional[str] = None


@dataclass
class AnnotationResult:
    entries: Dict[str, AnnotatedKey] = field(default_factory=dict)

    def by_status(self, status: str) -> list[AnnotatedKey]:
        return [e for e in self.entries.values() if e.status == status]


def annotate(first: dict, second: dict, diff: DiffResult) -> AnnotationResult:
    """Combine two env dicts with diff metadata into an AnnotationResult."""
    result = AnnotationResult()
    all_keys = set(first) | set(second)

    for key in sorted(all_keys):
        if key in diff.missing_in_second:
            entry = AnnotatedKey(
                key=key,
                value=first.get(key),
                status="missing_in_second",
                other_value=None,
            )
        elif key in diff.missing_in_first:
            entry = AnnotatedKey(
                key=key,
                value=None,
                status="missing_in_first",
                other_value=second.get(key),
            )
        elif key in diff.mismatched:
            entry = AnnotatedKey(
                key=key,
                value=first.get(key),
                status="mismatch",
                other_value=second.get(key),
            )
        else:
            entry = AnnotatedKey(
                key=key,
                value=first.get(key),
                status="ok",
                other_value=second.get(key),
            )
        result.entries[key] = entry

    return result
