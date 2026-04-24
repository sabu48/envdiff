"""Format AuditLog entries for human-readable or JSON output."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Literal

from envdiff.auditor import AuditLog


def _ts(timestamp: float) -> str:
    """Convert a POSIX timestamp to an ISO-8601 UTC string."""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def format_audit_text(log: AuditLog) -> str:
    if not log.entries:
        return "No audit entries found.\n"
    lines: list[str] = ["Audit Log", "=" * 40]
    for e in log.entries:
        files_str = ", ".join(e.files) if e.files else "(none)"
        lines.append(f"[{_ts(e.timestamp)}] {e.operation.upper()} | {e.outcome}")
        lines.append(f"  files  : {files_str}")
        if e.detail:
            lines.append(f"  detail : {e.detail}")
    lines.append("")
    return "\n".join(lines)


def format_audit_json(log: AuditLog) -> str:
    data = [
        {
            "timestamp": _ts(e.timestamp),
            "operation": e.operation,
            "files": e.files,
            "outcome": e.outcome,
            "detail": e.detail,
        }
        for e in log.entries
    ]
    return json.dumps(data, indent=2)


def render_audit(
    log: AuditLog,
    fmt: Literal["text", "json"] = "text",
) -> str:
    if fmt == "json":
        return format_audit_json(log)
    return format_audit_text(log)
