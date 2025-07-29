import datetime
import threading
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field
from enum import Enum
from types import TracebackType
from typing import Self, TypeVar

T = TypeVar("T")


class TaskLoggerUpdate(Enum):
    INTERVAL = 0
    """Update only at intervals (default)"""
    UPDATE = 1
    """Update on every call to update()"""
    ALL = 2
    """Update on every call to update() and at intervals"""


@dataclass(frozen=True)
class TaskLoggerMsg:
    start: str = "Starting task..."
    end: str = "Finished task in {duration}"
    end_w_size: str = "Finished task in {duration} ({duration_per_unit}/{unit})"
    progress: str = "Still running... (elapsed: {current}s)"
    progress_w_current: str = (
        "Still running... (elapsed: {current}s, processed: {current_size}{size_unit})"
    )
    progress_w_size_and_current: str = "Still running... (elapsed: {current}s, processed: {current_size}/{size}{size_unit})"


@dataclass
class BaseTaskLogger(ABC):
    name: str

    # --- Progress config ---
    size: int | None = None
    size_unit: str | tuple[str, str] = (" item", " items")
    progress_interval: float = 10
    progress_min_interval: float = 3
    progress_update: TaskLoggerUpdate = TaskLoggerUpdate.INTERVAL

    # --- Custom messaging ---
    msg: TaskLoggerMsg = field(default_factory=TaskLoggerMsg)

    # --- Control flags ---
    auto_start: bool = False
    on_error: Callable[[BaseException], None] | None = None

    # --- Internal state (not user-facing) ---
    _start: datetime.datetime = field(init=False)
    _current: int | None = field(default=None, init=False)
    _running: bool = field(default=False, init=False)
    _progress_thread: threading.Thread | None = field(default=None, init=False)
    _last_progress_time: float = field(default_factory=time.monotonic, init=False)
    _progress_lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def __post_init__(self):
        if self.size is not None and self.size < 0:
            raise ValueError("Size must be a non-negative integer or None.")
        if self.progress_interval <= 0:
            raise ValueError("Progress interval must be a positive number.")

        if self.auto_start:
            self.start()

    def start(self) -> Self:
        self._running = True
        self._start = datetime.datetime.now(tz=datetime.UTC)
        self._log_start()

        if self.progress_update in (TaskLoggerUpdate.INTERVAL, TaskLoggerUpdate.ALL):
            self._progress_thread = threading.Thread(
                target=self._progress_interval, daemon=True
            )
            self._progress_thread.start()

        return self

    def end(self):
        if not self._running:
            raise RuntimeError("TaskLogger has not been started or has already ended.")
        self._running = False
        duration = datetime.datetime.now(tz=datetime.UTC) - self._start

        self._log_end(duration)

    def update(self, current: int):
        if not self._running:
            raise RuntimeError("TaskLogger has not been started or has already ended.")
        with self._progress_lock:
            self._current = current

        if self.progress_update in (TaskLoggerUpdate.UPDATE, TaskLoggerUpdate.ALL):
            self._handle_log_progress()

    def iterate(self, iterable: Iterable[T]) -> Iterator[T]:
        self._current = 0
        for i, item in enumerate(iterable, 1):
            yield item
            self.update(i)

    def _progress_interval(self):
        while self._running:
            time.sleep(self.progress_interval)
            if not self._running:
                break
            self._handle_log_progress()

    def _handle_log_progress(self):
        now = time.monotonic()
        with self._progress_lock:
            if (now - self._last_progress_time) < self.progress_min_interval:
                return
            self._last_progress_time = now
            duration = datetime.datetime.now(tz=datetime.UTC) - self._start

            self._log_progress(
                now=now,
                duration=duration,
            )

    @abstractmethod
    def _log_start(self): ...

    @abstractmethod
    def _log_end(self, duration: datetime.timedelta): ...

    @abstractmethod
    def _log_exception(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ): ...

    @abstractmethod
    def _log_progress(self, now: float, duration: datetime.timedelta): ...

    def _plural_unit(self, current: int) -> str:
        if isinstance(self.size_unit, tuple):
            return self.size_unit[1 if current > 1 else 0]
        return self.size_unit

    def __enter__(self) -> Self:
        return self.start()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        self.end()
        if exc_val is not None:
            self._log_exception(exc_type, exc_val, exc_tb)
            if self.on_error:
                self.on_error(exc_val)
        return False  # propagate exception

    def __repr__(self):
        return f"<TaskLogger name={self.name!r} running={self._running}>"
