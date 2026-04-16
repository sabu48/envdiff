"""Utilities for sorting and grouping diff results by severity or key name."""

from __future__ import annotations

from enum import Enum
from typing import Dict, List, Tuple

from envdiff.comparator import DiffResult


class SortOrder(str, Enum):
    KEY = "key"
    SEVERITY = "severity"


# Severity ranking: missing keys are more severe than mismatches
_SEVERITY: Dict[str, int] = {
    "missing_in_second": 0,
    "missing_in_first": 1,
    "mismatched": 2,
}


def _severity_of(key: str, result: DiffResult) -> int:
    if key in result.missing_in_second:
        return _SEVERITY["missing_in_second"]
    if key in result.missing_in_first:
        return _SEVERITY["missing_in_first"]
    return _SEVERITY["mismatched"]


def all_diff_keys(result: DiffResult) -> List[str]:
    """Return every key that appears in any diff category."""
    return sorted(
        set(result.missing_in_first)
        | set(result.missing_in_second)
        | set(result.mismatched)
    )


def sort_diff(result: DiffResult, order: SortOrder = SortOrder.KEY) -> List[Tuple[str, str]]:
    """
    Return a list of (key, category) tuples sorted by *order*.

    category is one of: 'missing_in_first', 'missing_in_second', 'mismatched'.
    """
    entries: List[Tuple[str, str]] = []
    for key in result.missing_in_second:
        entries.append((key, "missing_in_second"))
    for key in result.missing_in_first:
        entries.append((key, "missing_in_first"))
    for key in result.mismatched:
        entries.append((key, "mismatched"))

    if order == SortOrder.KEY:
        entries.sort(key=lambda t: t[0])
    else:  # SEVERITY
        entries.sort(key=lambda t: (_SEVERITY[t[1]], t[0]))

    return entries
