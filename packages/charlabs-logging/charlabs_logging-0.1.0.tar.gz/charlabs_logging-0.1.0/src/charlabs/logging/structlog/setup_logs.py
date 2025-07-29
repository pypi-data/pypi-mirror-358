import logging
import sys

import structlog

from charlabs.logging._base.setup_logs import setup_log_exception_handler
from charlabs.logging.structlog.logs_settings import LogsExecEnvironment, LogsSettings
from charlabs.logging.structlog.processors import map_level_to_severity


def setup_logs(
    logs_settings: LogsSettings = LogsSettings(), *, is_dev: bool = False
) -> None:
    """Set up logging for the application."""
    level = logs_settings.dev_log_level if is_dev else logs_settings.log_level

    # Basic stdlib logging config
    logging.basicConfig(
        level=level,
        format="%(message)s",
        stream=sys.stdout,
    )

    # Select renderer
    renderer = (
        structlog.dev.ConsoleRenderer()
        if is_dev
        else structlog.processors.JSONRenderer()
    )

    # Shared processors
    pre_chain: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if not is_dev:
        pre_chain += [
            structlog.processors.format_exc_info,
            structlog.processors.CallsiteParameterAdder(
                {
                    structlog.processors.CallsiteParameter.MODULE,
                    structlog.processors.CallsiteParameter.FUNC_NAME,
                }
            ),
        ]
        if logs_settings.exec_environment == LogsExecEnvironment.GCP:
            pre_chain.append(map_level_to_severity)

    # Setup stdlib Formatter that wraps structlog processor chain
    formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=pre_chain,
    )

    # Apply formatter to all stdlib handlers
    for handler in logging.getLogger().handlers:
        handler.setFormatter(formatter)

    for logger_name in logs_settings.logger_names + logs_settings.logger_names_extends:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        for handler in logger.handlers:
            handler.setFormatter(formatter)

    # Configure structlog
    structlog.configure(
        processors=[
            *pre_chain,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )

    setup_log_exception_handler(
        structlog.get_logger(logs_settings.uncaught_log_name).critical
    )
