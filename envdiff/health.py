"""Health check module: aggregate issues across an env dict into a health report."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from envdiff.linter import lint_file
from envdiff.profiler import profile
from envdiff.secrets_scanner import scan


@dataclass
class HealthReport:
    path: str
    lint_issues: List[str] = field(default_factory=list)
    empty_keys: List[str] = field(default_factory=list)
    secret_hits: List[str] = field(default_factory=list)
    score: int = 100  # starts at 100, deductions applied

    @property
    def healthy(self) -> bool:
        return self.score >= 80

    def summary(self) -> str:
        parts = [f"Health score: {self.score}/100"]
        if self.lint_issues:
            parts.append(f"  Lint issues ({len(self.lint_issues)}): " + ", ".join(self.lint_issues))
        if self.empty_keys:
            parts.append(f"  Empty keys ({len(self.empty_keys)}): " + ", ".join(self.empty_keys))
        if self.secret_hits:
            parts.append(f"  Exposed secrets ({len(self.secret_hits)}): " + ", ".join(self.secret_hits))
        if self.healthy:
            parts.append("  Status: OK")
        else:
            parts.append("  Status: UNHEALTHY")
        return "\n".join(parts)


def check(path: str, env: Optional[Dict[str, Optional[str]]] = None) -> HealthReport:
    """Run all health checks against *path* and return a HealthReport."""
    report = HealthReport(path=path)

    # --- lint ---
    lint_result = lint_file(path)
    if not lint_result.ok():
        msgs = [i.message for i in lint_result.issues]
        report.lint_issues = msgs
        report.score -= min(30, len(msgs) * 5)

    # --- profiler (empty keys) ---
    if env is not None:
        prof = profile(env)
        if prof.has_issues():
            report.empty_keys = list(prof.empty_keys)
            report.score -= min(30, len(prof.empty_keys) * 5)

    # --- secrets scanner ---
    if env is not None:
        scan_result = scan(env)
        if not scan_result.clean():
            report.secret_hits = [h.key for h in scan_result.hits]
            report.score -= min(40, len(scan_result.hits) * 10)

    report.score = max(0, report.score)
    return report
