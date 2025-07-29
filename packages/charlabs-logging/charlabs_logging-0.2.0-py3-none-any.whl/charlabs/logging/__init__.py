from charlabs.logging import structlog
from charlabs.logging.default import LogsSettings, TaskLogger, setup_logs

__version__ = "0.2.0"

__all__ = [
    "structlog",
    "LogsSettings",
    "setup_logs",
    "TaskLogger",
    "__version__",
]
