"""Group env keys by prefix (e.g. DB_, AWS_, APP_) for structured reporting."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.comparator import DiffResult


@dataclass
class GroupReport:
    """Holds per-prefix groupings of diff keys."""
    groups: Dict[str, List[str]] = field(default_factory=dict)
    ungrouped: List[str] = field(default_factory=list)

    def all_prefixes(self) -> List[str]:
        return sorted(self.groups.keys())

    def keys_for(self, prefix: str) -> List[str]:
        return self.groups.get(prefix, [])


def _extract_prefix(key: str, separator: str = "_") -> Optional[str]:
    """Return the first segment before *separator*, or None if no separator."""
    if separator in key:
        return key.split(separator, 1)[0]
    return None


def all_diff_keys(result: DiffResult) -> List[str]:
    """Collect every key that appears in any diff category."""
    keys: set[str] = set()
    keys.update(result.missing_in_second)
    keys.update(result.missing_in_first)
    keys.update(result.mismatched)
    return sorted(keys)


def group_diff(
    result: DiffResult,
    separator: str = "_",
    min_group_size: int = 1,
) -> GroupReport:
    """Group all differing keys by their prefix.

    Keys without a prefix (or whose prefix group is smaller than
    *min_group_size*) are placed in *ungrouped*.
    """
    keys = all_diff_keys(result)
    buckets: Dict[str, List[str]] = {}

    for key in keys:
        prefix = _extract_prefix(key, separator)
        if prefix is not None:
            buckets.setdefault(prefix, []).append(key)
        else:
            buckets.setdefault("", []).append(key)

    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = []

    for prefix, members in buckets.items():
        if prefix == "" or len(members) < min_group_size:
            ungrouped.extend(members)
        else:
            groups[prefix] = sorted(members)

    return GroupReport(groups=groups, ungrouped=sorted(ungrouped))
