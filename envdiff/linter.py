"""Lint individual .env files for common style and correctness issues."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
import re


@dataclass
class LintIssue:
    line: int
    key: str | None
    code: str
    message: str


@dataclass
class LintResult:
    path: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return len(self.issues) == 0

    def summary(self) -> str:
        if self.ok:
            return f"{self.path}: no issues found"
        lines = [f"{self.path}: {len(self.issues)} issue(s)"]
        for iss in self.issues:
            loc = f"line {iss.line}" + (f" [{iss.key}]" if iss.key else "")
            lines.append(f"  {loc} {iss.code}: {iss.message}")
        return "\n".join(lines)


_VALID_KEY = re.compile(r'^[A-Z][A-Z0-9_]*$')


def lint_file(path: str) -> LintResult:
    result = LintResult(path=path)
    seen_keys: dict[str, int] = {}

    with open(path) as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in line:
                result.issues.append(LintIssue(lineno, None, "E001", f"no '=' found: {line!r}"))
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            if not _VALID_KEY.match(key):
                result.issues.append(LintIssue(lineno, key, "E002",
                    "key should be uppercase with underscores only"))
            if key in seen_keys:
                result.issues.append(LintIssue(lineno, key, "W001",
                    f"duplicate key (first seen on line {seen_keys[key]})"))
            else:
                seen_keys[key] = lineno
            if value != value.strip():
                result.issues.append(LintIssue(lineno, key, "W002",
                    "value has leading or trailing whitespace"))
    return result
