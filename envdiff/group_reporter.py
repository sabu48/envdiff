"""Render a GroupReport as text or JSON."""
from __future__ import annotations

import json
from typing import Literal

from envdiff.grouper import GroupReport


FormatType = Literal["text", "json"]


def _section(title: str, items: list[str]) -> str:
    if not items:
        return ""
    lines = [f"  [{title}]"] + [f"    {k}" for k in items]
    return "\n".join(lines)


def format_group_text(report: GroupReport) -> str:
    parts: list[str] = []

    for prefix in report.all_prefixes():
        keys = report.keys_for(prefix)
        parts.append(f"=== {prefix} ===")
        parts.append(_section("keys", keys))

    if report.ungrouped:
        parts.append("=== (ungrouped) ===")
        parts.append(_section("keys", report.ungrouped))

    if not parts:
        return "No differences found.\n"

    return "\n".join(filter(None, parts)) + "\n"


def format_group_json(report: GroupReport) -> str:
    data = {
        "groups": {p: report.keys_for(p) for p in report.all_prefixes()},
        "ungrouped": report.ungrouped,
    }
    return json.dumps(data, indent=2)


def render_group(report: GroupReport, fmt: FormatType = "text") -> str:
    if fmt == "json":
        return format_group_json(report)
    return format_group_text(report)
