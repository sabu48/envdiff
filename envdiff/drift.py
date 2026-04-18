"""Drift detection: compare current env files against a saved baseline snapshot."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.baseline import load_baseline, compare_to_baseline
from envdiff.parser import parse_env_file
from envdiff.comparator import DiffResult


@dataclass
class DriftReport:
    baseline_path: str
    env_path: str
    diff: DiffResult
    new_keys: List[str] = field(default_factory=list)
    removed_keys: List[str] = field(default_factory=list)
    changed_keys: List[str] = field(default_factory=list)

    @property
    def has_drift(self) -> bool:
        return bool(self.new_keys or self.removed_keys or self.changed_keys)

    def summary(self) -> str:
        if not self.has_drift:
            return "No drift detected."
        parts = []
        if self.new_keys:
            parts.append(f"{len(self.new_keys)} new key(s): {', '.join(self.new_keys)}")
        if self.removed_keys:
            parts.append(f"{len(self.removed_keys)} removed key(s): {', '.join(self.removed_keys)}")
        if self.changed_keys:
            parts.append(f"{len(self.changed_keys)} changed key(s): {', '.join(self.changed_keys)}")
        return "; ".join(parts)


def detect_drift(baseline_path: str, env_path: str) -> DriftReport:
    """Compare a live .env file against a saved baseline and return a DriftReport."""
    baseline: Dict[str, Optional[str]] = load_baseline(baseline_path)
    current: Dict[str, Optional[str]] = parse_env_file(env_path)

    diff: DiffResult = compare_to_baseline(baseline_path, current)

    baseline_keys = set(baseline.keys())
    current_keys = set(current.keys())

    new_keys = sorted(current_keys - baseline_keys)
    removed_keys = sorted(baseline_keys - current_keys)
    changed_keys = sorted(
        k for k in baseline_keys & current_keys if baseline.get(k) != current.get(k)
    )

    return DriftReport(
        baseline_path=baseline_path,
        env_path=env_path,
        diff=diff,
        new_keys=new_keys,
        removed_keys=removed_keys,
        changed_keys=changed_keys,
    )
