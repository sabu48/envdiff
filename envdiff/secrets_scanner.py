"""Scan .env files for potentially exposed secret values (e.g. hardcoded passwords)."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Patterns that suggest a value looks like a real secret (not a placeholder)
_PLACEHOLDER_RE = re.compile(
    r'^(change.?me|todo|placeholder|your[_-]?\w+|<[^>]+>|\$\{[^}]+\}|example|replace.?me)$',
    re.IGNORECASE,
)
_SENSITIVE_KEY_RE = re.compile(
    r'(password|passwd|secret|token|api[_-]?key|auth|credential|private[_-]?key|access[_-]?key)',
    re.IGNORECASE,
)


@dataclass
class SecretHit:
    key: str
    reason: str
    value_preview: str  # first 4 chars + '****'


@dataclass
class ScanResult:
    hits: List[SecretHit] = field(default_factory=list)
    scanned: int = 0

    @property
    def clean(self) -> bool:
        return len(self.hits) == 0

    def summary(self) -> str:
        if self.clean:
            return f"No exposed secrets found ({self.scanned} keys scanned)."
        lines = [f"{len(self.hits)} potential secret(s) found ({self.scanned} keys scanned):"]
        for h in self.hits:
            lines.append(f"  [{h.key}] {h.reason} — preview: {h.value_preview}")
        return "\n".join(lines)


def _value_preview(value: str) -> str:
    if not value:
        return "(empty)"
    return value[:4] + "****"


def _looks_like_real_secret(value: Optional[str]) -> bool:
    """Return True when the value appears to be a real (non-placeholder) secret."""
    if not value:
        return False
    if _PLACEHOLDER_RE.match(value.strip()):
        return False
    # Must have some non-trivial length
    return len(value.strip()) >= 8


def scan(env: Dict[str, Optional[str]]) -> ScanResult:
    """Scan a parsed env dict and return a ScanResult with any secret hits."""
    result = ScanResult(scanned=len(env))
    for key, value in env.items():
        if _SENSITIVE_KEY_RE.search(key):
            if _looks_like_real_secret(value):
                result.hits.append(
                    SecretHit(
                        key=key,
                        reason="sensitive key name with non-placeholder value",
                        value_preview=_value_preview(value or ""),
                    )
                )
    return result
