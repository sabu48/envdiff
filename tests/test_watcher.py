"""Tests for envdiff.watcher."""
import time
import pytest
from pathlib import Path

from envdiff.watcher import watch, ChangeEvent, _init_state


@pytest.fixture()
def tmp(tmp_path):
    return tmp_path


def _write(path: Path, content: str) -> None:
    path.write_text(content)


def test_init_state_reads_env(tmp):
    p = tmp / ".env"
    _write(p, "FOO=bar\nBAZ=qux\n")
    state = _init_state(str(p))
    assert state.last_env == {"FOO": "bar", "BAZ": "qux"}
    assert state.last_mtime > 0


def test_watch_detects_change(tmp):
    p = tmp / ".env"
    _write(p, "FOO=bar\n")

    events: list[ChangeEvent] = []

    def on_change(event: ChangeEvent) -> None:
        events.append(event)

    # Run one cycle before the write, then one after
    import threading

    def _modify():
        time.sleep(0.05)
        _write(p, "FOO=changed\nNEW=key\n")
        # bump mtime explicitly in case fs resolution is low
        future = time.time() + 2
        import os
        os.utime(str(p), (future, future))

    t = threading.Thread(target=_modify)
    t.start()
    watch([str(p)], on_change, interval=0.02, max_cycles=10)
    t.join()

    assert len(events) >= 1
    ev = events[0]
    assert ev.path == str(p)
    assert ev.current.get("FOO") == "changed"
    assert "NEW" in ev.current


def test_watch_no_change_no_event(tmp):
    p = tmp / ".env"
    _write(p, "FOO=bar\n")

    events: list[ChangeEvent] = []
    watch([str(p)], lambda e: events.append(e), interval=0.01, max_cycles=3)
    assert events == []


def test_change_event_diff_populated(tmp):
    p = tmp / ".env"
    _write(p, "FOO=bar\n")

    import os
    from envdiff.watcher import _init_state, ChangeEvent
    from envdiff.comparator import compare
    from envdiff.parser import parse_env_file

    state = _init_state(str(p))
    _write(p, "FOO=new\nEXTRA=yes\n")
    new_env = parse_env_file(str(p))
    diff = compare(state.last_env, new_env)
    ev = ChangeEvent(path=str(p), previous=state.last_env, current=new_env, diff=diff)

    assert "FOO" in ev.diff.mismatched
    assert "EXTRA" in ev.diff.missing_in_first
