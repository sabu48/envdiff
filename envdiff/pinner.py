"""Pin current env values as expected values and detect deviations."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class PinResult:
    pinned: Dict[str, Optional[str]]
    deviations: Dict[str, tuple]   # key -> (pinned_value, current_value)
    new_keys: List[str]
    removed_keys: List[str]

    def has_deviations(self) -> bool:
        return bool(self.deviations or self.new_keys or self.removed_keys)

    def summary(self) -> str:
        parts = []
        if self.deviations:
            parts.append(f"{len(self.deviations)} deviated")
        if self.new_keys:
            parts.append(f"{len(self.new_keys)} new")
        if self.removed_keys:
            parts.append(f"{len(self.removed_keys)} removed")
        return ", ".join(parts) if parts else "no deviations"


def pin(env: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    """Return a snapshot of env values to use as the pin baseline."""
    return dict(env)


def save_pin(env: Dict[str, Optional[str]], path: Path) -> None:
    """Persist pinned values to a JSON file."""
    path.write_text(json.dumps(env, indent=2, default=str), encoding="utf-8")


def load_pin(path: Path) -> Dict[str, Optional[str]]:
    """Load pinned values from a JSON file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: (None if v is None else str(v)) for k, v in data.items()}


def check_pin(
    pinned: Dict[str, Optional[str]],
    current: Dict[str, Optional[str]],
) -> PinResult:
    """Compare current env against pinned baseline and return a PinResult."""
    pinned_keys = set(pinned)
    current_keys = set(current)

    deviations: Dict[str, tuple] = {}
    for key in pinned_keys & current_keys:
        if pinned[key] != current[key]:
            deviations[key] = (pinned[key], current[key])

    new_keys = sorted(current_keys - pinned_keys)
    removed_keys = sorted(pinned_keys - current_keys)

    return PinResult(
        pinned=pinned,
        deviations=deviations,
        new_keys=new_keys,
        removed_keys=removed_keys,
    )
