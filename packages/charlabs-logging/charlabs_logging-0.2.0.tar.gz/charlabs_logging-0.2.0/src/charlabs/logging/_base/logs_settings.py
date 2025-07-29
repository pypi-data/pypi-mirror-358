from pydantic import Field
from pydantic_settings import BaseSettings


class BaseLogsSettings(BaseSettings):
    uncaught_log_name: str = Field(
        default="uncaught_exception",
        description="The name of the logger used for uncaught exceptions. This logger will be configured with the log level specified in `log_level`.",
    )
