"""Format snapshot diff results for display."""

from __future__ import annotations

import json
from typing import Dict


def _section(title: str, items: Dict[str, object]) -> str:
    if not items:
        return ""
    lines = [f"  [{title}]"]
    for key, val in items.items():
        if isinstance(val, dict) and "old" in val:
            lines.append(f"    {key}: {val['old']!r} -> {val['new']!r}")
        else:
            lines.append(f"    {key}={val!r}")
    return "\n".join(lines)


def format_snapshot_text(diff: Dict[str, Dict[str, object]]) -> str:
    """Render snapshot diff as human-readable text."""
    if not diff:
        return "No changes detected between snapshots.\n"

    parts = []
    for env_name, changes in sorted(diff.items()):
        parts.append(f"=== {env_name} ===")
        for category in ("added", "removed", "changed"):
            section = _section(category.upper(), changes.get(category, {}))
            if section:
                parts.append(section)
    return "\n".join(parts) + "\n"


def format_snapshot_json(diff: Dict[str, Dict[str, object]]) -> str:
    """Render snapshot diff as JSON."""
    return json.dumps(diff, indent=2)


def render_snapshot_diff(
    diff: Dict[str, Dict[str, object]], fmt: str = "text"
) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "json":
        return format_snapshot_json(diff)
    return format_snapshot_text(diff)
