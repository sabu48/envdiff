"""Resolve variable interpolation references within .env files.

Supports ${VAR} and $VAR style references.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

_BRACE_RE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")
_BARE_RE = re.compile(r"\$([A-Za-z_][A-Za-z0-9_]*)")


@dataclass
class InterpolateResult:
    resolved: Dict[str, Optional[str]]
    unresolved_refs: List[str]  # keys whose values still contain unresolved refs
    cycles: List[str]           # keys involved in circular references

    def is_clean(self) -> bool:
        return not self.unresolved_refs and not self.cycles

    def summary(self) -> str:
        parts: List[str] = []
        if self.unresolved_refs:
            parts.append(f"unresolved refs in: {', '.join(sorted(self.unresolved_refs))}")
        if self.cycles:
            parts.append(f"cycles detected for: {', '.join(sorted(self.cycles))}")
        return "; ".join(parts) if parts else "all references resolved"


def _refs_in(value: Optional[str]) -> List[str]:
    """Return all variable names referenced inside *value*."""
    if not value:
        return []
    names = _BRACE_RE.findall(value) + _BARE_RE.findall(value)
    return list(dict.fromkeys(names))  # deduplicate, preserve order


def _resolve_value(
    key: str,
    env: Dict[str, Optional[str]],
    cache: Dict[str, Optional[str]],
    visiting: set,
    cycles: set,
) -> Optional[str]:
    if key in cache:
        return cache[key]
    if key not in env:
        return None
    if key in visiting:
        cycles.add(key)
        return env[key]  # return raw to avoid infinite loop
    visiting.add(key)
    raw = env[key]
    if not raw:
        cache[key] = raw
        visiting.discard(key)
        return raw

    def _replace_brace(m: re.Match) -> str:
        ref = m.group(1)
        resolved = _resolve_value(ref, env, cache, visiting, cycles)
        return resolved if resolved is not None else m.group(0)

    def _replace_bare(m: re.Match) -> str:
        ref = m.group(1)
        resolved = _resolve_value(ref, env, cache, visiting, cycles)
        return resolved if resolved is not None else m.group(0)

    result = _BRACE_RE.sub(_replace_brace, raw)
    result = _BARE_RE.sub(_replace_bare, result)
    cache[key] = result
    visiting.discard(key)
    return result


def interpolate(env: Dict[str, Optional[str]]) -> InterpolateResult:
    """Resolve all ${VAR}/$VAR references in *env* and return an InterpolateResult."""
    cache: Dict[str, Optional[str]] = {}
    cycles: set = set()

    resolved: Dict[str, Optional[str]] = {}
    for key in env:
        resolved[key] = _resolve_value(key, env, cache, set(), cycles)

    unresolved_refs = [
        k for k, v in resolved.items() if v and bool(_BRACE_RE.search(v) or _BARE_RE.search(v))
    ]
    return InterpolateResult(
        resolved=resolved,
        unresolved_refs=unresolved_refs,
        cycles=list(cycles),
    )
