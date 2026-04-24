"""Deduplicator: merge duplicate keys across multiple env dicts by applying a resolution strategy."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DeduplicateResult:
    """Result of deduplicating multiple env dicts into one."""
    resolved: Dict[str, Optional[str]]
    conflicts: Dict[str, List[Optional[str]]]  # key -> all distinct values seen
    sources: Dict[str, int]  # key -> index of env dict that won

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def conflict_summary(self) -> str:
        if not self.conflicts:
            return "No conflicts."
        lines = [f"{k}: {vals}" for k, vals in sorted(self.conflicts.items())]
        return "Conflicts:\n" + "\n".join(f"  {l}" for l in lines)


def deduplicate(
    envs: List[Dict[str, Optional[str]]],
    strategy: str = "last",
    ignore_keys: Optional[List[str]] = None,
) -> DeduplicateResult:
    """Deduplicate keys across *envs* using the given *strategy*.

    Strategies:
        - ``"first"``  – keep the value from the first env that defines the key.
        - ``"last"``   – keep the value from the last env that defines the key (default).
        - ``"strict"`` – like ``"first"`` but records any key whose value differs across
                         envs as a conflict (value in *resolved* is still the first).

    Keys listed in *ignore_keys* are copied verbatim from the first env that contains
    them and are never recorded as conflicts.
    """
    if strategy not in ("first", "last", "strict"):
        raise ValueError(f"Unknown strategy {strategy!r}; choose 'first', 'last', or 'strict'.")

    ignore = set(ignore_keys or [])
    resolved: Dict[str, Optional[str]] = {}
    sources: Dict[str, int] = {}
    all_values: Dict[str, List[Optional[str]]] = {}

    for idx, env in enumerate(envs):
        for key, value in env.items():
            if key not in all_values:
                all_values[key] = []
            all_values[key].append(value)

            if strategy == "last":
                resolved[key] = value
                sources[key] = idx
            else:  # "first" or "strict"
                if key not in resolved:
                    resolved[key] = value
                    sources[key] = idx

    conflicts: Dict[str, List[Optional[str]]] = {}
    if strategy == "strict":
        for key, vals in all_values.items():
            if key in ignore:
                continue
            distinct = list(dict.fromkeys(vals))  # preserve order, dedupe
            if len(distinct) > 1:
                conflicts[key] = distinct

    return DeduplicateResult(resolved=resolved, conflicts=conflicts, sources=sources)
