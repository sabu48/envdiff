"""Watch .env files for changes and report drift in real time."""
from __future__ import annotations

import time
import os
from dataclasses import dataclass, field
from typing import Callable, Dict, Optional

from envdiff.parser import parse_env_file
from envdiff.comparator import compare, DiffResult


@dataclass
class WatchState:
    path: str
    last_mtime: float
    last_env: Dict[str, Optional[str]]


@dataclass
class ChangeEvent:
    path: str
    previous: Dict[str, Optional[str]]
    current: Dict[str, Optional[str]]
    diff: DiffResult


def _mtime(path: str) -> float:
    return os.path.getmtime(path)


def _init_state(path: str) -> WatchState:
    env = parse_env_file(path)
    return WatchState(path=path, last_mtime=_mtime(path), last_env=env)


def watch(
    paths: list[str],
    on_change: Callable[[ChangeEvent], None],
    interval: float = 1.0,
    max_cycles: Optional[int] = None,
) -> None:
    """Poll *paths* every *interval* seconds; call *on_change* when a file changes."""
    states: Dict[str, WatchState] = {p: _init_state(p) for p in paths}
    cycles = 0
    while max_cycles is None or cycles < max_cycles:
        time.sleep(interval)
        for path, state in states.items():
            try:
                mt = _mtime(path)
            except FileNotFoundError:
                continue
            if mt != state.last_mtime:
                new_env = parse_env_file(path)
                diff = compare(state.last_env, new_env)
                event = ChangeEvent(
                    path=path,
                    previous=state.last_env,
                    current=new_env,
                    diff=diff,
                )
                on_change(event)
                states[path] = WatchState(path=path, last_mtime=mt, last_env=new_env)
        cycles += 1
