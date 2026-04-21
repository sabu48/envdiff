"""Snapshot multiple .env files into a single timestamped archive."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file


@dataclass
class Snapshot:
    created_at: float
    envs: Dict[str, Dict[str, Optional[str]]]
    labels: List[str] = field(default_factory=list)

    def env_names(self) -> List[str]:
        return list(self.envs.keys())

    def get(self, name: str) -> Dict[str, Optional[str]]:
        return self.envs.get(name, {})


def take_snapshot(
    paths: List[str],
    labels: Optional[List[str]] = None,
) -> Snapshot:
    """Parse each path and bundle results into a Snapshot."""
    envs: Dict[str, Dict[str, Optional[str]]] = {}
    resolved_labels = labels or []

    for i, path in enumerate(paths):
        name = resolved_labels[i] if i < len(resolved_labels) else Path(path).name
        envs[name] = parse_env_file(path)

    return Snapshot(created_at=time.time(), envs=envs, labels=list(envs.keys()))


def save_snapshot(snapshot: Snapshot, dest: str) -> None:
    """Persist a snapshot to a JSON file."""
    payload = {
        "created_at": snapshot.created_at,
        "labels": snapshot.labels,
        "envs": {
            name: {k: v for k, v in env.items()}
            for name, env in snapshot.envs.items()
        },
    }
    Path(dest).write_text(json.dumps(payload, indent=2))


def load_snapshot(src: str) -> Snapshot:
    """Load a snapshot from a JSON file."""
    data = json.loads(Path(src).read_text())
    envs = {
        name: {k: (v if v is not None else None) for k, v in env.items()}
        for name, env in data["envs"].items()
    }
    return Snapshot(
        created_at=data["created_at"],
        envs=envs,
        labels=data.get("labels", list(envs.keys())),
    )


def diff_snapshots(
    old: Snapshot, new: Snapshot
) -> Dict[str, Dict[str, object]]:
    """Return per-env key-level changes between two snapshots."""
    result: Dict[str, Dict[str, object]] = {}
    all_names = set(old.env_names()) | set(new.env_names())
    for name in all_names:
        old_env = old.get(name)
        new_env = new.get(name)
        added = {k: new_env[k] for k in new_env if k not in old_env}
        removed = {k: old_env[k] for k in old_env if k not in new_env}
        changed = {
            k: {"old": old_env[k], "new": new_env[k]}
            for k in old_env
            if k in new_env and old_env[k] != new_env[k]
        }
        if added or removed or changed:
            result[name] = {"added": added, "removed": removed, "changed": changed}
    return result
