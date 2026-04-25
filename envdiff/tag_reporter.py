"""Format TagResult objects for human-readable and JSON output."""
from __future__ import annotations

import json
from typing import Optional

from envdiff.tagger import TagResult


def _section(title: str, lines: list[str]) -> str:
    header = f"[{title}]"
    return "\n".join([header] + lines) + "\n"


def format_tag_text(result: TagResult) -> str:
    parts: list[str] = []

    for tag_name in result.tag_map.all_tags():
        subset = result.tagged(tag_name)
        if not subset:
            continue
        lines = [f"  {k}={v if v is not None else ''}" for k, v in sorted(subset.items())]
        parts.append(_section(tag_name, lines))

    untagged = result.untagged()
    if untagged:
        lines = [f"  {k}={v if v is not None else ''}" for k, v in sorted(untagged.items())]
        parts.append(_section("untagged", lines))

    return "".join(parts) if parts else "No keys.\n"


def format_tag_json(result: TagResult) -> str:
    data: dict = {}

    for tag_name in result.tag_map.all_tags():
        subset = result.tagged(tag_name)
        if subset:
            data[tag_name] = {k: v for k, v in sorted(subset.items())}

    untagged = result.untagged()
    if untagged:
        data["untagged"] = {k: v for k, v in sorted(untagged.items())}

    return json.dumps(data, indent=2)


def render_tag(result: TagResult, fmt: str = "text") -> str:
    if fmt == "json":
        return format_tag_json(result)
    return format_tag_text(result)
