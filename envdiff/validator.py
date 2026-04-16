"""Validate .env files against a schema of required keys."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class ValidationResult:
    missing_required: List[str] = field(default_factory=list)
    invalid_values: Dict[str, str] = field(default_factory=dict)  # key -> reason

    @property
    def is_valid(self) -> bool:
        return not self.missing_required and not self.invalid_values

    def summary(self) -> str:
        parts = []
        if self.missing_required:
            parts.append(f"Missing required keys: {', '.join(sorted(self.missing_required))}")
        if self.invalid_values:
            for k, reason in sorted(self.invalid_values.items()):
                parts.append(f"Invalid value for '{k}': {reason}")
        return "\n".join(parts) if parts else "All validations passed."


@dataclass
class KeySchema:
    required: Set[str] = field(default_factory=set)
    # optional regex pattern per key name
    patterns: Dict[str, str] = field(default_factory=dict)


def validate(
    env: Dict[str, Optional[str]],
    schema: KeySchema,
) -> ValidationResult:
    """Validate an env dict against a KeySchema."""
    import re

    result = ValidationResult()

    for key in schema.required:
        if key not in env or env[key] is None or env[key] == "":
            result.missing_required.append(key)

    for key, pattern in schema.patterns.items():
        if key in env and env[key] is not None:
            if not re.fullmatch(pattern, env[key]):
                result.invalid_values[key] = f"does not match pattern '{pattern}'"

    return result
