"""Format PinResult as text or JSON for CLI output."""
from __future__ import annotations

import json
from typing import Literal

from envdiff.pinner import PinResult


def _section(title: str, lines: list[str]) -> str:
    block = "\n".join(f"  {l}" for l in lines)
    return f"{title}\n{block}\n"


def format_pin_text(result: PinResult) -> str:
    if not result.has_deviations():
        return "No deviations from pin.\n"

    parts: list[str] = []

    if result.deviations:
        lines = [
            f"{k}: pinned={v[0]!r}  current={v[1]!r}"
            for k, v in sorted(result.deviations.items())
        ]
        parts.append(_section("Deviated keys:", lines))

    if result.new_keys:
        parts.append(_section("New keys (not in pin):", result.new_keys))

    if result.removed_keys:
        parts.append(_section("Removed keys (missing from current):", result.removed_keys))

    return "".join(parts)


def format_pin_json(result: PinResult) -> str:
    payload = {
        "has_deviations": result.has_deviations(),
        "summary": result.summary(),
        "deviations": {
            k: {"pinned": v[0], "current": v[1]}
            for k, v in sorted(result.deviations.items())
        },
        "new_keys": result.new_keys,
        "removed_keys": result.removed_keys,
    }
    return json.dumps(payload, indent=2)


def render_pin(
    result: PinResult,
    fmt: Literal["text", "json"] = "text",
) -> str:
    if fmt == "json":
        return format_pin_json(result)
    return format_pin_text(result)
