"""changelog.py – generate a human-readable changelog between two env snapshots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.snapshotter import Snapshot


@dataclass
class ChangelogEntry:
    env_name: str
    added: Dict[str, str] = field(default_factory=dict)
    removed: Dict[str, str] = field(default_factory=dict)
    changed: Dict[str, tuple] = field(default_factory=dict)  # key -> (old, new)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


@dataclass
class ChangelogReport:
    entries: List[ChangelogEntry] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return any(e.has_changes for e in self.entries)

    def summary(self) -> str:
        if not self.has_changes:
            return "No changes detected between snapshots."
        lines = []
        for entry in self.entries:
            if not entry.has_changes:
                continue
            lines.append(f"[{entry.env_name}]")
            for k, v in entry.added.items():
                lines.append(f"  + {k}={v}")
            for k, v in entry.removed.items():
                lines.append(f"  - {k}={v}")
            for k, (old, new) in entry.changed.items():
                lines.append(f"  ~ {k}: {old!r} -> {new!r}")
        return "\n".join(lines)


def _diff_envs(
    old: Optional[Dict[str, Optional[str]]],
    new: Optional[Dict[str, Optional[str]]],
) -> ChangelogEntry:
    """Compare two env dicts (may be None if env absent in a snapshot)."""
    old = old or {}
    new = new or {}
    added = {k: (v or "") for k, v in new.items() if k not in old}
    removed = {k: (v or "") for k, v in old.items() if k not in new}
    changed = {
        k: (old[k], new[k])
        for k in old.keys() & new.keys()
        if old[k] != new[k]
    }
    return added, removed, changed


def build_changelog(before: Snapshot, after: Snapshot) -> ChangelogReport:
    """Produce a ChangelogReport comparing *before* to *after* snapshots."""
    all_envs = set(before.env_names()) | set(after.env_names())
    entries: List[ChangelogEntry] = []
    for name in sorted(all_envs):
        old_env = before.get(name)
        new_env = after.get(name)
        added, removed, changed = _diff_envs(old_env, new_env)
        entries.append(
            ChangelogEntry(
                env_name=name,
                added=added,
                removed=removed,
                changed=changed,
            )
        )
    return ChangelogReport(entries=entries)
