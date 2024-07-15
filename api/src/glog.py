import logging
from typing import Any

from pythonjsonlogger import jsonlogger


class Formatter(jsonlogger.JsonFormatter):
    """
    Custom log formatter that emits log messages as JSON, with the "severity" field
    which Google Cloud uses to differentiate message levels.
    """

    def add_fields(
        self,
        log_record: dict[str, Any],
        record: logging.LogRecord,
        message_dict: dict[str, Any],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["severity"] = record.levelname


class Handler(logging.StreamHandler):
    def __init__(self, stream=None) -> None:
        super().__init__(stream)
        self.setFormatter(Formatter())
