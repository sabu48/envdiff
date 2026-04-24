"""Audit trail: record and replay diff operations with timestamps."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional


@dataclass
class AuditEntry:
    timestamp: float
    operation: str          # e.g. "diff", "validate", "lint", "merge"
    files: List[str]
    outcome: str            # "ok" | "differences" | "error"
    detail: Optional[str] = None


@dataclass
class AuditLog:
    entries: List[AuditEntry] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.entries)

    def since(self, cutoff: float) -> "AuditLog":
        """Return a new AuditLog with only entries at or after *cutoff*."""
        return AuditLog([e for e in self.entries if e.timestamp >= cutoff])

    def by_operation(self, operation: str) -> "AuditLog":
        return AuditLog([e for e in self.entries if e.operation == operation])


def record(log: AuditLog, operation: str, files: List[str],
           outcome: str, detail: Optional[str] = None) -> AuditEntry:
    """Append a new entry to *log* and return it."""
    entry = AuditEntry(
        timestamp=time.time(),
        operation=operation,
        files=list(files),
        outcome=outcome,
        detail=detail,
    )
    log.entries.append(entry)
    return entry


def save_audit_log(log: AuditLog, path: Path) -> None:
    """Persist *log* to a JSON file at *path*."""
    data = [asdict(e) for e in log.entries]
    path.write_text(json.dumps(data, indent=2))


def load_audit_log(path: Path) -> AuditLog:
    """Load an AuditLog from a JSON file at *path*."""
    data = json.loads(path.read_text())
    entries = [
        AuditEntry(
            timestamp=d["timestamp"],
            operation=d["operation"],
            files=d["files"],
            outcome=d["outcome"],
            detail=d.get("detail"),
        )
        for d in data
    ]
    return AuditLog(entries)
