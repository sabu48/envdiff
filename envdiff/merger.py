"""Merge multiple .env files into a unified dict with conflict tracking."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class MergeResult:
    merged: Dict[str, str] = field(default_factory=dict)
    conflicts: Dict[str, List[Tuple[str, Optional[str]]]] = field(default_factory=dict)
    sources: List[str] = field(default_factory=list)

    def has_conflicts(self) -> bool:
        return bool(self.conflicts)

    def conflict_summary(self) -> str:
        if not self.conflicts:
            return "No conflicts."
        lines = [f"{len(self.conflicts)} conflict(s) detected:"]
        for key, entries in self.conflicts.items():
            for src, val in entries:
                lines.append(f"  [{src}] {key}={val!r}")
        return "\n".join(lines)


def merge(
    envs: Dict[str, Dict[str, Optional[str]]],
    strategy: str = "last",
) -> MergeResult:
    """Merge env dicts.

    Args:
        envs: mapping of source_name -> parsed env dict.
        strategy: 'last' uses last seen value; 'first' keeps first value.
    """
    if strategy not in ("last", "first"):
        raise ValueError(f"Unknown strategy {strategy!r}. Use 'first' or 'last'.")

    result = MergeResult(sources=list(envs.keys()))
    seen: Dict[str, Tuple[str, Optional[str]]] = {}

    for source, env in envs.items():
        for key, value in env.items():
            if key in seen:
                prev_src, prev_val = seen[key]
                if prev_val != value:
                    result.conflicts.setdefault(key, [])
                    if not result.conflicts[key]:
                        result.conflicts[key].append((prev_src, prev_val))
                    result.conflicts[key].append((source, value))
                    if strategy == "last":
                        seen[key] = (source, value)
            else:
                seen[key] = (source, value)

    result.merged = {k: v for k, (_, v) in seen.items()}
    return result
