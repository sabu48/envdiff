"""Baseline management: save and compare against a stored env snapshot."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional

from envdiff.comparator import DiffResult, compare


def save_baseline(env: Dict[str, Optional[str]], path: str) -> None:
    """Persist an env dict as a JSON baseline file."""
    Path(path).write_text(json.dumps(env, indent=2, sort_keys=True))


def load_baseline(path: str) -> Dict[str, Optional[str]]:
    """Load a previously saved baseline from a JSON file."""
    raw = json.loads(Path(path).read_text())
    # JSON nulls become Python None; everything else stays a string
    return {k: (None if v is None else str(v)) for k, v in raw.items()}


def compare_to_baseline(
    current: Dict[str, Optional[str]],
    baseline_path: str,
) -> DiffResult:
    """Compare *current* env dict against a saved baseline.

    Returns a DiffResult where:
      - missing_in_second  = keys present in current but absent in baseline
      - missing_in_first   = keys present in baseline but absent in current
      - mismatched         = keys whose values changed since the baseline
    """
    baseline = load_baseline(baseline_path)
    return compare(current, baseline)
