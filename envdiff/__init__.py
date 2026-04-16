"""envdiff — compare .env files across environments."""

from envdiff.parser import parse_env_file
from envdiff.comparator import compare, DiffResult
from envdiff.reporter import render

__all__ = [
    "parse_env_file",
    "compare",
    "DiffResult",
    "render",
]

__version__ = "0.1.0"
