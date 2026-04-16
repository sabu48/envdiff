"""Export diff results to various file formats (JSON, CSV, Markdown)."""
from __future__ import annotations

import csv
import io
import json
from typing import Literal

from envdiff.comparator import DiffResult

ExportFormat = Literal["json", "csv", "markdown"]


def export_json(result: DiffResult) -> str:
    """Serialise a DiffResult to a JSON string."""
    data = {
        "missing_in_second": sorted(result.missing_in_second),
        "missing_in_first": sorted(result.missing_in_first),
        "mismatched": {
            k: {"first": v[0], "second": v[1]}
            for k, v in sorted(result.mismatched.items())
        },
    }
    return json.dumps(data, indent=2)


def export_csv(result: DiffResult) -> str:
    """Serialise a DiffResult to a CSV string."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["key", "category", "value_first", "value_second"])
    for key in sorted(result.missing_in_second):
        writer.writerow([key, "missing_in_second", "", ""])
    for key in sorted(result.missing_in_first):
        writer.writerow([key, "missing_in_first", "", ""])
    for key, (v1, v2) in sorted(result.mismatched.items()):
        writer.writerow([key, "mismatched", v1, v2])
    return buf.getvalue()


def export_markdown(result: DiffResult) -> str:
    """Serialise a DiffResult to a Markdown table string."""
    lines: list[str] = []
    lines.append("| Key | Category | Value (first) | Value (second) |")
    lines.append("|-----|----------|---------------|----------------|")
    for key in sorted(result.missing_in_second):
        lines.append(f"| `{key}` | missing_in_second | | |")
    for key in sorted(result.missing_in_first):
        lines.append(f"| `{key}` | missing_in_first | | |")
    for key, (v1, v2) in sorted(result.mismatched.items()):
        lines.append(f"| `{key}` | mismatched | `{v1}` | `{v2}` |")
    return "\n".join(lines) + "\n"


_EXPORTERS = {
    "json": export_json,
    "csv": export_csv,
    "markdown": export_markdown,
}


def export(result: DiffResult, fmt: ExportFormat) -> str:
    """Dispatch to the correct exporter; raise ValueError for unknown formats."""
    try:
        return _EXPORTERS[fmt](result)
    except KeyError:
        raise ValueError(f"Unknown export format: {fmt!r}. Choose from {list(_EXPORTERS)}.")
