import datetime
from dataclasses import dataclass, field
from types import TracebackType
from typing import TypeVar

import structlog

from charlabs.logging._base.task_logger import (
    BaseTaskLogger,
)

T = TypeVar("T")


@dataclass
class TaskLogger(BaseTaskLogger):
    logger: structlog.BoundLogger = field(
        default_factory=lambda: structlog.get_logger("task_logger")
    )

    def __post_init__(self):
        super().__post_init__()
        self.logger = self.logger.bind(task_name=self.name)

        if self.progress_min_interval > self.progress_interval:
            self.logger.warning(
                "progress_min_interval is greater than progress_interval, "
                "this may lead to unexpected behavior.",
                progress_min_interval=self.progress_min_interval,
                progress_interval=self.progress_interval,
            )

    def _log_start(self):
        self.logger.info(self.msg.start, task_status="started")

    def _log_end(self, duration: datetime.timedelta):
        log = self.logger.bind(
            duration=f"{duration.total_seconds():.0f}s",
            task_status="stopped",
        )

        if self.size and self.size > 0:
            log.info(
                self.msg.end_w_size.format(
                    duration=duration,
                    duration_per_unit=duration / self.size,
                    unit=self._plural_unit(self.size),
                )
            )
        else:
            log.info(self.msg.end.format(duration=duration))

    def _log_progress(self, now: float, duration: datetime.timedelta):
        log = self.logger.bind(
            task_elapsed=f"{duration.total_seconds():.0f}s",
            task_status="running",
        )

        if self._current is not None:
            log = log.bind(
                task_current=self._current,
            )
            if self.size is not None and self.size > 0:
                log.info(
                    self.msg.progress_w_size_and_current.format(
                        current=round(duration.total_seconds()),
                        current_size=self._current,
                        size=self.size,
                        size_unit=self._plural_unit(self.size),
                    ),
                    task_total=self.size,
                    task_progress=f"{self._current / self.size:.0%}",
                )
            else:
                log.info(
                    self.msg.progress_w_current.format(
                        current=round(duration.total_seconds()),
                        current_size=self._current,
                        size_unit=self._plural_unit(self._current),
                    )
                )
        else:
            log.info(self.msg.progress.format(current=round(duration.total_seconds())))

    def _log_exception(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        self.logger.error(
            "Task failed with error",
            task_status="failed",
            error=str(exc_val),
            exc_info=(exc_type, exc_val, exc_tb),  # noqa: LOG014
        )
