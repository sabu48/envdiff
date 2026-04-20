"""Normalize .env values for comparison (strip quotes, whitespace, case-fold keys)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class NormalizeResult:
    original: Dict[str, Optional[str]]
    normalized: Dict[str, Optional[str]]
    changes: Dict[str, str]  # key -> human-readable description of what changed


def _normalize_key(key: str) -> str:
    """Upper-case and strip surrounding whitespace from a key."""
    return key.strip().upper()


def _normalize_value(value: Optional[str]) -> Optional[str]:
    """Strip surrounding whitespace and remove matching outer quotes from a value."""
    if value is None:
        return None
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        value = value[1:-1]
    return value


def normalize(env: Dict[str, Optional[str]]) -> NormalizeResult:
    """Return a NormalizeResult with normalized keys and values.

    Normalisation rules applied:
    - Keys are upper-cased and whitespace-stripped.
    - Values are whitespace-stripped and outer quote pairs are removed.
    """
    original: Dict[str, Optional[str]] = dict(env)
    normalized: Dict[str, Optional[str]] = {}
    changes: Dict[str, str] = {}

    for raw_key, raw_value in env.items():
        norm_key = _normalize_key(raw_key)
        norm_value = _normalize_value(raw_value)

        descriptions = []
        if norm_key != raw_key:
            descriptions.append(f"key cased '{raw_key}' -> '{norm_key}'")
        if norm_value != raw_value:
            descriptions.append(f"value changed '{raw_value}' -> '{norm_value}'")

        normalized[norm_key] = norm_value
        if descriptions:
            changes[norm_key] = "; ".join(descriptions)

    return NormalizeResult(original=original, normalized=normalized, changes=changes)


def normalize_many(
    envs: Dict[str, Dict[str, Optional[str]]]
) -> Dict[str, NormalizeResult]:
    """Normalize a mapping of env-name -> env dict, returning per-name NormalizeResults."""
    return {name: normalize(env) for name, env in envs.items()}
