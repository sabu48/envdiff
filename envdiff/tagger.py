"""Tag keys in .env files with custom labels for categorisation and filtering."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Optional


@dataclass
class TagMap:
    """Mapping of tag name -> set of keys that carry that tag."""
    _data: Dict[str, FrozenSet[str]] = field(default_factory=dict)

    def add(self, tag: str, keys: List[str]) -> None:
        existing = set(self._data.get(tag, frozenset()))
        existing.update(keys)
        self._data[tag] = frozenset(existing)

    def tags_for(self, key: str) -> FrozenSet[str]:
        return frozenset(t for t, keys in self._data.items() if key in keys)

    def keys_for(self, tag: str) -> FrozenSet[str]:
        return self._data.get(tag, frozenset())

    def all_tags(self) -> List[str]:
        return sorted(self._data.keys())


@dataclass
class TagResult:
    env: Dict[str, Optional[str]]
    tag_map: TagMap

    def tagged(self, tag: str) -> Dict[str, Optional[str]]:
        """Return subset of env whose keys carry *tag*."""
        wanted = self.tag_map.keys_for(tag)
        return {k: v for k, v in self.env.items() if k in wanted}

    def untagged(self) -> Dict[str, Optional[str]]:
        """Return subset of env whose keys carry no tag."""
        all_tagged = frozenset().union(*self.tag_map._data.values()) if self.tag_map._data else frozenset()
        return {k: v for k, v in self.env.items() if k not in all_tagged}


def tag(env: Dict[str, Optional[str]], tag_map: TagMap) -> TagResult:
    """Apply *tag_map* to *env* and return a TagResult."""
    return TagResult(env=dict(env), tag_map=tag_map)


def build_tag_map(rules: Dict[str, List[str]]) -> TagMap:
    """Build a TagMap from a plain dict of {tag: [key, ...]}."""
    tm = TagMap()
    for tag_name, keys in rules.items():
        tm.add(tag_name, keys)
    return tm
