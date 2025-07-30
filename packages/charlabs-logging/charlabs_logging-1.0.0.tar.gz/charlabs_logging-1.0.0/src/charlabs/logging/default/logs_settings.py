from pathlib import Path

from pydantic import Field, FilePath

from charlabs.logging._base.logs_settings import BaseLogsSettings


class LogsSettings(BaseLogsSettings):
    logs_config_path: FilePath = Field(
        default=Path("conf/logging.yaml"),
        description=(
            "Path to the logging configuration file. "
            "The file should follow the [logging configuration dictionary schema](https://docs.python.org/3/library/logging.config.html#logging-config-dictschema)"
        ),
    )
