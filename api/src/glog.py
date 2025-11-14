import logging
from datetime import datetime
from typing import TextIO

from pythonjsonlogger.json import JsonFormatter as pjlJsonFormatter


class JsonFormatter(pjlJsonFormatter):
    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None):
        # Format the timestamp as RFC 3339 with microsecond precision
        isoformat = datetime.fromtimestamp(record.created).isoformat()
        return f"{isoformat}Z"


# taken from https://cloud.google.com/trace/docs/setup/python-ot#config-structured-logging
def create_stream_handler() -> logging.StreamHandler[TextIO]:
    handler = logging.StreamHandler()
    """
    Custom log formatter that emits log messages as JSON, with the "severity" field
    which Google Cloud uses to differentiate message levels and various opentelemetry mappings.
    """
    formatter = JsonFormatter(
        "%(asctime)s %(levelname)s %(message)s %(otelTraceID)s %(otelSpanID)s %(otelTraceSampled)s",
        rename_fields={
            "levelname": "severity",
            "asctime": "timestamp",
            "otelTraceID": "logging.googleapis.com/trace",
            "otelSpanID": "logging.googleapis.com/spanId",
            "otelTraceSampled": "logging.googleapis.com/trace_sampled",
        },
    )
    handler.setFormatter(formatter)

    return handler
