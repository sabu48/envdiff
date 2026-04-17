"""High-level diff pipeline: parse, filter, sort, and return results."""
from pathlib import Path
from typing import Optional, List

from envdiff.parser import parse_env_file
from envdiff.comparator import compare, DiffResult
from envdiff.filter import filter_diff
from envdiff.sorter import sort_diff, SortOrder


def diff_files(
    path_a: str,
    path_b: str,
    pattern: Optional[str] = None,
    category: Optional[str] = None,
    sort: SortOrder = SortOrder.KEY,
) -> DiffResult:
    """Parse two .env files and return a filtered, sorted DiffResult."""
    env_a = parse_env_file(Path(path_a))
    env_b = parse_env_file(Path(path_b))
    result = compare(env_a, env_b)
    result = filter_diff(result, pattern=pattern, category=category)
    result = sort_diff(result, order=sort)
    return result


def diff_many(
    paths: List[str],
    baseline: int = 0,
    pattern: Optional[str] = None,
    category: Optional[str] = None,
    sort: SortOrder = SortOrder.KEY,
) -> List[DiffResult]:
    """Diff a baseline .env file against each of the remaining files.

    Args:
        paths: List of file paths; the file at *baseline* index is the reference.
        baseline: Index in *paths* to treat as the reference environment.
        pattern: Optional glob/regex pattern to filter keys.
        category: Optional category filter ('missing_in_second', 'missing_in_first',
                  'mismatched').
        sort: Sort order for keys in each result.

    Returns:
        A list of DiffResult objects (one per non-baseline file).
    """
    if len(paths) < 2:
        raise ValueError("At least two file paths are required.")
    if baseline < 0 or baseline >= len(paths):
        raise IndexError(f"baseline index {baseline} out of range for {len(paths)} files.")

    results = []
    for i, path in enumerate(paths):
        if i == baseline:
            continue
        results.append(
            diff_files(paths[baseline], path, pattern=pattern, category=category, sort=sort)
        )
    return results
