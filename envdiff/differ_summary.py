"""Combine diff + summarize into a single pipeline step."""
from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.differ import diff_many
from envdiff.summarizer import EnvSummary, summarize
from envdiff.comparator import DiffResult


@dataclass
class DiffSummaryReport:
    """Holds both pairwise diffs and per-env summaries."""
    diffs: Dict[str, DiffResult] = field(default_factory=dict)
    summary: EnvSummary = None

    @property
    def has_any_differences(self) -> bool:
        from envdiff.comparator import has_differences
        return any(has_differences(d) for d in self.diffs.values())

    def env_names(self) -> List[str]:
        return list(self.summary.env_names) if self.summary else []


def build_report(env_paths: Dict[str, str]) -> DiffSummaryReport:
    """Parse all envs, compute pairwise diffs, and summarize.

    Args:
        env_paths: mapping of label -> file path

    Returns:
        DiffSummaryReport with diffs and summary populated.
    """
    from envdiff.parser import parse_env_file

    envs: Dict[str, Dict[str, str]] = {
        label: parse_env_file(path)
        for label, path in env_paths.items()
    }

    diffs = diff_many(env_paths)
    env_summary = summarize(envs)

    return DiffSummaryReport(diffs=diffs, summary=env_summary)
