"""Score how similar two env files are based on key overlap and value matches."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict

from envdiff.comparator import DiffResult


@dataclass
class SimilarityScore:
    total_keys: int
    common_keys: int
    matching_values: int
    key_overlap: float   # 0.0 – 1.0
    value_match: float   # 0.0 – 1.0  (out of common keys)
    overall: float       # weighted composite

    def __str__(self) -> str:
        return (
            f"overall={self.overall:.2f} "
            f"key_overlap={self.key_overlap:.2f} "
            f"value_match={self.value_match:.2f}"
        )


def score(result: DiffResult) -> SimilarityScore:
    """Compute a similarity score from a DiffResult."""
    only_first = set(result.missing_in_second)  # keys in base but not in target
    only_second = set(result.missing_in_first)  # keys in target but not in base
    mismatched = set(result.mismatched.keys())  # keys present in both but with different values
    matching = set(result.matching.keys())  # keys present in both with identical values

    common_keys = matching | mismatched
    all_keys = common_keys | only_first | only_second

    total = len(all_keys)
    common = len(common_keys)
    matched_vals = len(matching)

    key_overlap = common / total if total else 1.0
    value_match = matched_vals / common if common else 1.0
    overall = round(0.5 * key_overlap + 0.5 * value_match, 4)

    return SimilarityScore(
        total_keys=total,
        common_keys=common,
        matching_values=matched_vals,
        key_overlap=round(key_overlap, 4),
        value_match=round(value_match, 4),
        overall=overall,
    )


def score_many(results: Dict[str, DiffResult]) -> Dict[str, SimilarityScore]:
    """Score multiple DiffResults keyed by a label (e.g. 'a_vs_b')."""
    return {label: score(r) for label, r in results.items()}
