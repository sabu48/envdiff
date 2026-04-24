"""scheduler.py — schedule periodic drift checks and emit events.

Provides a lightweight polling scheduler that runs drift detection
against a baseline on a configurable interval, calling a user-supplied
callback whenever drift is detected.
"""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

from envdiff.drift import DriftReport, detect_drift


@dataclass
class ScheduleConfig:
    """Configuration for a scheduled drift check."""

    env_file: Path
    baseline_file: Path
    interval_seconds: float = 60.0
    max_runs: Optional[int] = None  # None means run indefinitely
    stop_on_drift: bool = False


@dataclass
class ScheduleRun:
    """Result of a single scheduled run."""

    run_number: int
    timestamp: float
    report: DriftReport
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


@dataclass
class SchedulerState:
    """Mutable state tracked across scheduler lifetime."""

    runs: List[ScheduleRun] = field(default_factory=list)
    stopped: bool = False
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False, compare=False)

    def record(self, run: ScheduleRun) -> None:
        with self._lock:
            self.runs.append(run)

    def stop(self) -> None:
        with self._lock:
            self.stopped = True

    @property
    def is_stopped(self) -> bool:
        with self._lock:
            return self.stopped

    @property
    def total_runs(self) -> int:
        with self._lock:
            return len(self.runs)

    @property
    def drift_runs(self) -> List[ScheduleRun]:
        with self._lock:
            return [r for r in self.runs if r.ok and r.report.has_drift]


def _single_check(env_file: Path, baseline_file: Path) -> DriftReport:
    """Run one drift check and return the report."""
    return detect_drift(env_file, baseline_file)


def run_scheduler(
    config: ScheduleConfig,
    on_drift: Optional[Callable[[ScheduleRun], None]] = None,
    on_run: Optional[Callable[[ScheduleRun], None]] = None,
) -> SchedulerState:
    """Start a blocking scheduler that polls for drift.

    Args:
        config: Schedule configuration (files, interval, limits).
        on_drift: Optional callback invoked when drift is detected.
        on_run: Optional callback invoked after every run (drift or not).

    Returns:
        SchedulerState populated with all run results after the scheduler
        exits (either because max_runs was reached, stop_on_drift triggered,
        or the caller interrupted via KeyboardInterrupt).
    """
    state = SchedulerState()
    run_number = 0

    try:
        while not state.is_stopped:
            run_number += 1
            timestamp = time.time()
            error: Optional[str] = None
            report: Optional[DriftReport] = None

            try:
                report = _single_check(config.env_file, config.baseline_file)
            except Exception as exc:  # noqa: BLE001
                error = str(exc)
                # Build an empty non-drift report so ScheduleRun is always valid
                from envdiff.drift import DriftReport as _DR
                report = _DR(new_keys=[], removed_keys=[], changed_keys={})

            run = ScheduleRun(
                run_number=run_number,
                timestamp=timestamp,
                report=report,
                error=error,
            )
            state.record(run)

            if on_run is not None:
                on_run(run)

            if run.ok and report.has_drift:
                if on_drift is not None:
                    on_drift(run)
                if config.stop_on_drift:
                    state.stop()
                    break

            if config.max_runs is not None and run_number >= config.max_runs:
                state.stop()
                break

            if not state.is_stopped:
                time.sleep(config.interval_seconds)

    except KeyboardInterrupt:
        state.stop()

    return state
