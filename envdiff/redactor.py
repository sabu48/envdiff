"""Redact sensitive values in env diffs before display or export."""
from __future__ import annotations

import re
from typing import Dict, List, Optional

DEFAULT_PATTERNS = [
    re.compile(r"(password|passwd|secret|token|api_key|private_key|auth)", re.IGNORECASE),
]

REDACTED = "***REDACTED***"


def _is_sensitive(key: str, extra_patterns: Optional[list] = None) -> bool:
    patterns = DEFAULT_PATTERNS + (extra_patterns or [])
    return any(p.search(key) for p in patterns)


def compile_patterns(patterns: List[str]) -> List[re.Pattern]:
    """Compile a list of regex strings into pattern objects.

    Convenience helper so callers don't need to import ``re`` just to
    pass extra patterns to :func:`redact_env` or :func:`redact_diff`.

    Args:
        patterns: List of regular expression strings.

    Returns:
        List of compiled :class:`re.Pattern` objects.
    """
    return [re.compile(p, re.IGNORECASE) for p in patterns]


def redact_env(
    env: Dict[str, Optional[str]],
    extra_patterns: Optional[list] = None,
) -> Dict[str, Optional[str]]:
    """Return a copy of env with sensitive values replaced by REDACTED."""
    return {
        k: (REDACTED if _is_sensitive(k, extra_patterns) and v is not None else v)
        for k, v in env.items()
    }


def redact_diff(
    diff: dict,
    extra_patterns: Optional[list] = None,
) -> dict:
    """Redact sensitive values inside a DiffResult-like mapping.

    Accepts the dict representation produced by comparator.compare and
    returns a new dict with sensitive values replaced.
    """
    def _clean(key: str, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return REDACTED if _is_sensitive(key, extra_patterns) else value

    result: dict = {}
    for category in ("missing_in_second", "missing_in_first"):
        result[category] = list(diff.get(category, []))

    mismatched = {}
    for k, (v1, v2) in diff.get("mismatched", {}).items():
        mismatched[k] = (_clean(k, v1), _clean(k, v2))
    result["mismatched"] = mismatched

    matched = {}
    for k, v in diff.get("matched", {}).items():
        matched[k] = _clean(k, v)
    result["matched"] = matched

    return result


def sensitive_keys(env: Dict[str, Optional[str]], extra_patterns: Optional[list] = None) -> List[str]:
    """Return a sorted list of keys in *env* that match sensitive patterns.

    Useful for auditing which variables will be redacted before actually
    performing redaction.

    Args:
        env: Mapping of environment variable names to their values.
        extra_patterns: Additional compiled patterns beyond the defaults.

    Returns:
        Sorted list of sensitive key names found in *env*.
    """
    return sorted(k for k in env if _is_sensitive(k, extra_patterns))
