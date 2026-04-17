"""Summarize diff results across multiple environments."""
from dataclasses import dataclass, field
from typing import Dict, List
from envdiff.comparator import DiffResult


@dataclass
class EnvSummary:
    env_names: List[str] = field(default_factory=list)
    total_keys: int = 0
    common_keys: List[str] = field(default_factory=list)
    all_missing: Dict[str, List[str]] = field(default_factory=dict)  # key -> envs missing it
    all_mismatched: List[str] = field(default_factory=list)
    per_pair: Dict[str, DiffResult] = field(default_factory=dict)

    def has_issues(self) -> bool:
        return bool(self.all_missing or self.all_mismatched)


def summarize(env_maps: Dict[str, Dict[str, str]]) -> EnvSummary:
    """Given a mapping of env_name -> parsed env dict, produce an EnvSummary."""
    from envdiff.comparator import compare

    names = list(env_maps.keys())
    all_keys: set = set()
    for env in env_maps.values():
        all_keys.update(env.keys())

    common = [k for k in all_keys if all(k in env_maps[n] for n in names)]

    missing: Dict[str, List[str]] = {}
    for key in all_keys:
        absent = [n for n in names if key not in env_maps[n] or env_maps[n][key] is None]
        if absent:
            missing[key] = absent

    mismatched = []
    for key in common:
        values = {env_maps[n][key] for n in names}
        if len(values) > 1:
            mismatched.append(key)

    per_pair: Dict[str, DiffResult] = {}
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            a, b = names[i], names[j]
            label = f"{a}:{b}"
            per_pair[label] = compare(env_maps[a], env_maps[b])

    return EnvSummary(
        env_names=names,
        total_keys=len(all_keys),
        common_keys=sorted(common),
        all_missing=missing,
        all_mismatched=sorted(mismatched),
        per_pair=per_pair,
    )
