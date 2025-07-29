import asyncio
import sys
import threading
from types import TracebackType
from typing import Any, Protocol


class SetupLogFn(Protocol):
    def __call__(self, msg: Any, *, exc_info: Any, **kwargs: Any) -> None:
        """Function to set up logging with a message and exception type."""


def setup_log_exception_handler(log_fn: SetupLogFn) -> None:
    def handle_exception(
        exc_type: type[BaseException],
        exc_value: BaseException,
        exc_traceback: TracebackType | None,
    ) -> None:
        if issubclass(exc_type, KeyboardInterrupt):
            return sys.__excepthook__(exc_type, exc_value, exc_traceback)
        log_fn(
            "uncaught_exception",
            exc_info=(exc_type, exc_value, exc_traceback),  # noqa: LOG014
        )
        return None

    sys.excepthook = handle_exception

    def thread_exception_handler(args: threading.ExceptHookArgs):
        log_fn(
            "uncaught_thread_exception",
            thread=args.thread.name if args.thread else "unknown",
            exc_info=(args.exc_type, args.exc_value, args.exc_traceback),  # noqa: LOG014
        )

    threading.excepthook = thread_exception_handler

    def async_exception_handler(_: Any, context: dict[str, Any]):
        msg = context.get("message", "unhandled_asyncio_exception")
        exc = context.get("exception")
        log_fn(msg, exc_info=exc)

    asyncio.get_event_loop().set_exception_handler(async_exception_handler)
