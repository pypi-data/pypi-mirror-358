from typing import Any

import structlog


def map_level_to_severity(
    _logger: Any, _method_name: str, event_dict: structlog.typing.EventDict
) -> structlog.typing.EventDict:
    level = event_dict.pop("level", None)
    if level:
        event_dict["severity"] = level.upper()
    return event_dict
