"""Formats and outputs DiffResult comparisons in human-readable or machine-readable form."""

from __future__ import annotations

import json
from typing import Literal

from envdiff.comparator import DiffResult

OutputFormat = Literal["text", "json"]


def _section(title: str, items: list[str], bullet: str = "  - ") -> list[str]:
    if not items:
        return []
    lines = [f"{title}:"]
    for item in sorted(items):
        lines.append(f"{bullet}{item}")
    return lines


def format_text(result: DiffResult, file_a: str = "A", file_b: str = "B") -> str:
    """Return a human-readable diff report."""
    if not result.has_differences():
        return f"✓ No differences found between {file_a} and {file_b}.\n"

    lines: list[str] = [f"Differences between {file_a} and {file_b}:", ""]

    lines += _section(f"Missing in {file_b}", result.missing_in_second)
    if result.missing_in_second:
        lines.append("")

    lines += _section(f"Missing in {file_a}", result.missing_in_first)
    if result.missing_in_first:
        lines.append("")

    if result.mismatched_values:
        lines.append("Mismatched values:")
        for key in sorted(result.mismatched_values):
            val_a, val_b = result.mismatched_values[key]
            lines.append(f"  - {key}: {val_a!r} ({file_a}) vs {val_b!r} ({file_b})")
        lines.append("")

    lines.append(result.summary())
    return "\n".join(lines) + "\n"


def format_json(result: DiffResult, file_a: str = "A", file_b: str = "B") -> str:
    """Return a JSON-serialisable diff report as a string."""
    payload = {
        "files": {"a": file_a, "b": file_b},
        "has_differences": result.has_differences(),
        "missing_in_second": sorted(result.missing_in_second),
        "missing_in_first": sorted(result.missing_in_first),
        "mismatched_values": {
            k: {"a": v[0], "b": v[1]}
            for k, v in sorted(result.mismatched_values.items())
        },
        "summary": result.summary(),
    }
    return json.dumps(payload, indent=2)


def render(result: DiffResult, file_a: str = "A", file_b: str = "B",
           fmt: OutputFormat = "text") -> str:
    """Render a DiffResult in the requested format."""
    if fmt == "json":
        return format_json(result, file_a, file_b)
    return format_text(result, file_a, file_b)
