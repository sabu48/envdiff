"""Filter DiffResult entries by key pattern or category."""

from __future__ import annotations

import fnmatch
from typing import Optional, Sequence

from envdiff.comparator import DiffResult


def filter_diff(
    result: DiffResult,
    *,
    patterns: Optional[Sequence[str]] = None,
    categories: Optional[Sequence[str]] = None,
) -> DiffResult:
    """
    Return a new DiffResult containing only entries whose key matches at least
    one glob *pattern* (if provided) and whose category is in *categories*
    (if provided).

    Valid categories: 'missing_in_first', 'missing_in_second', 'mismatched'.
    """
    allowed_cats = set(categories) if categories else {"missing_in_first", "missing_in_second", "mismatched"}

    def _keep(key: str) -> bool:
        if patterns:
            return any(fnmatch.fnmatch(key, p) for p in patterns)
        return True

    missing_in_first = (
        {k: v for k, v in result.missing_in_first.items() if _keep(k)}
        if "missing_in_first" in allowed_cats
        else {}
    )
    missing_in_second = (
        {k: v for k, v in result.missing_in_second.items() if _keep(k)}
        if "missing_in_second" in allowed_cats
        else {}
    )
    mismatched = (
        {k: v for k, v in result.mismatched.items() if _keep(k)}
        if "mismatched" in allowed_cats
        else {}
    )

    # common is not a diff category — preserve as-is
    return DiffResult(
        missing_in_first=missing_in_first,
        missing_in_second=missing_in_second,
        mismatched=mismatched,
        common=result.common,
    )
