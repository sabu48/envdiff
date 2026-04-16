"""Parser for .env files."""

import re
from pathlib import Path
from typing import Dict, Optional


ENV_LINE_RE = re.compile(
    r'^\s*(?P<key>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*)\s*$'
)


def parse_env_file(path: str | Path) -> Dict[str, Optional[str]]:
    """Parse a .env file and return a dict of key-value pairs.

    - Lines starting with '#' are treated as comments and skipped.
    - Empty lines are skipped.
    - Values may be optionally quoted with single or double quotes;
      surrounding quotes are stripped.
    - Keys without a value (e.g. ``KEY=``) are stored as empty string.

    Args:
        path: Path to the .env file.

    Returns:
        Ordered dict mapping variable names to their string values.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f".env file not found: {path}")

    result: Dict[str, Optional[str]] = {}

    with path.open(encoding="utf-8") as fh:
        for raw_line in fh:
            line = raw_line.strip()

            # Skip blank lines and comments
            if not"#"):
                continue

            match = ENV_LINE_RE.match(line)
            if not match:
                # Ignore malformed lines silently
                continue

            key = match.group("key")
            value = match.group("value").strip()

            # Strip optional surrounding quotes
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]

            result[key] = value

    return result
