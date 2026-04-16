"""Register 'merge' as a formatter plugin and expose merge summary format."""
from __future__ import annotations
from typing import Any, Dict
import json

from envdiff.plugins import register_formatter
from envdiff.merger import MergeResult


def _format_merge_text(result: MergeResult, **_: Any) -> str:
    lines = [f"Sources: {', '.join(result.sources)}"]
    lines.append(f"Total keys: {len(result.merged)}")
    if result.has_conflicts():
        lines.append(result.conflict_summary())
    else:
        lines.append("No conflicts.")
    merged_lines = [f"{k}={v}" for k, v in sorted(result.merged.items()) if v is not None]
    lines.append("\n--- Merged ---")
    lines.extend(merged_lines)
    return "\n".join(lines)


def _format_merge_json(result: MergeResult, **_: Any) -> str:
    payload: Dict[str, Any] = {
        "sources": result.sources,
        "merged": result.merged,
        "conflicts": {
            k: [{"source": s, "value": v} for s, v in entries]
            for k, entries in result.conflicts.items()
        },
    }
    return json.dumps(payload, indent=2)


def register_merge_formatters() -> None:
    register_formatter("merge-text", _format_merge_text)
    register_formatter("merge-json", _format_merge_json)


register_merge_formatters()
