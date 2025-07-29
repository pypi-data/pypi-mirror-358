import logging.config
from pathlib import Path

import yaml

from charlabs.logging._base.setup_logs import setup_log_exception_handler

from .logs_settings import LogsSettings


def setup_logs(logs_settings: LogsSettings):
    with Path.open(logs_settings.logs_config_path, "r") as file:
        log_config = yaml.safe_load(file)

    logging.config.dictConfig(log_config)

    logger = logging.getLogger(logs_settings.uncaught_log_name)
    setup_log_exception_handler(logger.critical)  # type: ignore[no-untyped-call]
