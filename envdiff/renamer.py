"""Key renaming/aliasing support for env diff results."""
from dataclasses import dataclass, field
from typing import Dict, Optional
from envdiff.comparator import DiffResult


@dataclass
class RenameMap:
    """Maps old key names to new key names."""
    mappings: Dict[str, str] = field(default_factory=dict)

    def add(self, old: str, new: str) -> None:
        self.mappings[old] = new

    def apply(self, key: str) -> str:
        return self.mappings.get(key, key)


def load_rename_map(path: str) -> RenameMap:
    """Load a rename map from a simple KEY=ALIAS file."""
    rm = RenameMap()
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            old, new = line.split("=", 1)
            rm.add(old.strip(), new.strip())
    return rm


def apply_rename(diff: DiffResult, rename_map: RenameMap) -> DiffResult:
    """Return a new DiffResult with keys renamed according to rename_map."""
    def _remap(d: dict) -> dict:
        return {rename_map.apply(k): v for k, v in d.items()}

    def _remap_set(s: set) -> set:
        return {rename_map.apply(k) for k in s}

    return DiffResult(
        missing_in_second=_remap_set(diff.missing_in_second),
        missing_in_first=_remap_set(diff.missing_in_first),
        mismatched=_remap(diff.mismatched),
        identical=_remap_set(diff.identical),
    )
