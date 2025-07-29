import logging
from enum import Enum

from pydantic import Field

from charlabs.logging._base.logs_settings import BaseLogsSettings


class LogsExecEnvironment(Enum):
    GCP = "gcp"


class LogsSettings(BaseLogsSettings):
    log_level: int | str = Field(
        default=logging.INFO,
        description="The log level for the application. Can be an integer or a string like 'DEBUG', 'INFO', etc.",
    )
    dev_log_level: int | str = Field(
        default=logging.DEBUG,
        description="The log level for the application in development mode.",
    )

    exec_environment: LogsExecEnvironment | None = Field(
        default=None,
        description="The execution environment of the application, e.g., GCP. Some cloud providers may require specific logging configurations.",
    )

    logger_names: list[str] = Field(
        default_factory=lambda: [
            "root",
            "uvicorn",
            "uvicorn.error",
            "uvicorn.access",
            "gunicorn",
            "fastapi",
            "sqlalchemy.engine",
            "sqlalchemy.orm",
            "sqlalchemy.poolstarlette",
            "asyncio",
            "httpx",
            "botocore",
            "boto3",
            "google",
        ],
        description="List of logger names to configure. These loggers will be set up with the specified log level.",
    )
    logger_names_extends: list[str] = Field(
        default_factory=list,
        description="List of additional logger names to configure. Use this to extend the default logger names with custom ones.",
    )
