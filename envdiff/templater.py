"""Generate a .env.template file from one or more parsed env dicts."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class TemplateResult:
    keys: List[str]
    descriptions: Dict[str, str] = field(default_factory=dict)

    def render(self, placeholder: str = "") -> str:
        lines: List[str] = []
        for key in self.keys:
            desc = self.descriptions.get(key)
            if desc:
                lines.append(f"# {desc}")
            lines.append(f"{key}={placeholder}")
        return "\n".join(lines) + "\n"


def build_template(
    *envs: Dict[str, Optional[str]],
    descriptions: Optional[Dict[str, str]] = None,
    sort_keys: bool = True,
) -> TemplateResult:
    """Collect all unique keys from one or more env dicts into a template."""
    seen: dict = {}
    for env in envs:
        for key in env:
            seen[key] = True

    keys = sorted(seen) if sort_keys else list(seen)
    return TemplateResult(keys=keys, descriptions=descriptions or {})


def save_template(result: TemplateResult, path: str, placeholder: str = "") -> None:
    with open(path, "w") as fh:
        fh.write(result.render(placeholder=placeholder))


def load_template_keys(path: str) -> List[str]:
    """Return the list of keys defined in a template file (values ignored)."""
    keys: List[str] = []
    with open(path) as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                keys.append(line.split("=", 1)[0].strip())
    return keys
