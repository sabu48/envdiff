"""Profile an env file: count keys, detect duplicates, empty values, and long values."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List
from envdiff.parser import parse_env_file


@dataclass
class ProfileResult:
    path: str
    total_keys: int
    empty_keys: List[str]
    duplicate_keys: List[str]
    long_keys: List[str]  # values exceeding max_value_len
    key_lengths: Dict[str, int]  # key -> len(value or "")

    def has_issues(self) -> bool:
        return bool(self.empty_keys or self.duplicate_keys or self.long_keys)

    def summary(self) -> str:
        parts = [f"total={self.total_keys}"]
        if self.empty_keys:
            parts.append(f"empty={len(self.empty_keys)}")
        if self.duplicate_keys:
            parts.append(f"duplicates={len(self.duplicate_keys)}")
        if self.long_keys:
            parts.append(f"long={len(self.long_keys)}")
        return ", ".join(parts)


def profile(path: str, max_value_len: int = 256) -> ProfileResult:
    """Parse *path* and return a ProfileResult."""
    env = parse_env_file(path)

    # Detect duplicates by re-reading raw lines
    seen: Dict[str, int] = {}
    duplicates: List[str] = []
    try:
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key = line.split("=", 1)[0].strip()
                    seen[key] = seen.get(key, 0) + 1
    except OSError:
        pass
    duplicates = [k for k, count in seen.items() if count > 1]

    empty_keys = [k for k, v in env.items() if v is None or v == ""]
    long_keys = [k for k, v in env.items() if v and len(v) > max_value_len]
    key_lengths = {k: len(v) if v else 0 for k, v in env.items()}

    return ProfileResult(
        path=path,
        total_keys=len(env),
        empty_keys=empty_keys,
        duplicate_keys=duplicates,
        long_keys=long_keys,
        key_lengths=key_lengths,
    )
