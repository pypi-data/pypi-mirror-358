import logging
from dataclasses import dataclass
from datetime import timedelta
from types import TracebackType

from charlabs.logging._base.task_logger import BaseTaskLogger


@dataclass
class TaskLogger(BaseTaskLogger):
    logger: logging.Logger = logging.getLogger("task_logger")
    level: int = logging.INFO
    log_template: str = "[Task: %s] %s"

    def _log_start(self):
        self._log(self.msg.start)

    def _log_end(self, duration: timedelta):
        if self.size and self.size > 0:
            msg = self.msg.end_w_size.format(
                duration=duration,
                duration_per_unit=duration / self.size,
                unit=self._plural_unit(self.size),
            )
        else:
            msg = self.msg.end.format(duration=duration)

        self._log(msg)

    def _log_progress(self, now: float, duration: timedelta):
        if self.size and self._current is not None:
            self._log(
                self.msg.progress_w_size_and_current.format(
                    current=f"{duration.total_seconds():.0f}",
                    current_size=self._current,
                    size=self.size,
                    size_unit=self._plural_unit(self._current),
                )
            )
        elif self._current is not None:
            self._log(
                self.msg.progress_w_current.format(
                    current=f"{duration.total_seconds():.0f}",
                    current_size=self._current,
                    size_unit=self._plural_unit(self._current),
                )
            )
        else:
            self._log(
                self.msg.progress.format(current=f"{duration.total_seconds():.0f}")
            )

    def _log_exception(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if exc_type is None or exc_val is None:
            return

        self.logger.critical(
            self.log_template,
            self.name,
            f"Task failed with error: {exc_val}",
            exc_info=(exc_type, exc_val, exc_tb),  # noqa: LOG014
            extra={"task_name": self.name},
        )

    def _log(self, message: str):
        self.logger.log(
            self.level,
            self.log_template,
            self.name,
            message,
            extra={"task_name": self.name},
        )
