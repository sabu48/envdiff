"""Compare parsed .env file dictionaries and report differences."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class DiffResult:
    """Holds the comparison result between two .env files."""

    missing_in_second: List[str] = field(default_factory=list)
    missing_in_first: List[str] = field(default_factory=list)
    mismatched: Dict[str, Dict[str, Optional[str]]] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.missing_in_second or self.missing_in_first or self.mismatched
        )

    def summary(self, label_first: str = "first", label_second: str = "second") -> str:
        lines = []
        if self.missing_in_second:
            lines.append(f"Keys missing in {label_second}:")
            for key in sorted(self.missing_in_second):
                lines.append(f"  - {key}")
        if self.missing_in_first:
            lines.append(f"Keys missing in {label_first}:")
            for key in sorted(self.missing_in_first):
                lines.append(f"  - {key}")
        if self.mismatched:
            lines.append("Mismatched values:")
            for key in sorted(self.mismatched):
                a = self.mismatched[key]["first"]
                b = self.mismatched[key]["second"]
                lines.append(f"  ~ {key}: {a!r} != {b!r}")
        if not lines:
            lines.append("No differences found.")
        return "\n".join(lines)


def compare(
    first: Dict[str, Optional[str]],
    second: Dict[str, Optional[str]],
) -> DiffResult:
    """Compare two env dictionaries and return a DiffResult."""
    result = DiffResult()

    all_keys = set(first) | set(second)

    for key in all_keys:
        in_first = key in first
        in_second = key in second

        if in_first and not in_second:
            result.missing_in_second.append(key)
        elif in_second and not in_first:
            result.missing_in_first.append(key)
        elif first[key] != second[key]:
            result.mismatched[key] = {"first": first[key], "second": second[key]}

    return result
