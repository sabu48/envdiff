"""Simple plugin registry for custom output formatters.

Third-party packages can register a formatter by calling::

    from envdiff.plugins import register_formatter

    register_formatter("myformat", my_format_fn)

The function signature must match ``format_text`` / ``format_json`` in
``envdiff.reporter``::

    def my_format_fn(result: DiffResult) -> str: ...
"""

from __future__ import annotations

from typing import Callable, Dict

from envdiff.comparator import DiffResult

FormatterFn = Callable[[DiffResult], str]

_registry: Dict[str, FormatterFn] = {}


def register_formatter(name: str, fn: FormatterFn) -> None:
    """Register *fn* under *name*. Raises ValueError if name is already taken."""
    if name in _registry:
        raise ValueError(f"Formatter '{name}' is already registered.")
    _registry[name] = fn


def get_formatter(name: str) -> FormatterFn:
    """Return the formatter registered under *name*. Raises KeyError if absent."""
    try:
        return _registry[name]
    except KeyError:
        available = ", ".join(sorted(_registry)) or "<none>"
        raise KeyError(f"No formatter named '{name}'. Available: {available}") from None


def list_formatters() -> list[str]:
    """Return sorted list of registered formatter names."""
    return sorted(_registry)


def unregister_formatter(name: str) -> None:
    """Remove a formatter (useful in tests)."""
    _registry.pop(name, None)
