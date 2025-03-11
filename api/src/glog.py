import logging
from typing import TextIO

from pythonjsonlogger import jsonlogger


def create_stream_handler() -> logging.StreamHandler[TextIO]:
    handler = logging.StreamHandler()
    """
    Custom log formatter that emits log messages as JSON, with the "severity" field
    which Google Cloud uses to differentiate message levels and various opentelemetry mappings.
    """
    formatter = jsonlogger.JsonFormatter(
        # taken from https://cloud.google.com/trace/docs/setup/python-ot#config-structured-logging
        "%(asctime)s %(levelname)s %(message)s %(otelTraceID)s %(otelSpanID)s %(otelTraceSampled)s",
        rename_fields={
            "levelname": "severity",
            "asctime": "timestamp",
            "otelTraceID": "logging.googleapis.com/trace",
            "otelSpanID": "logging.googleapis.com/spanId",
            "otelTraceSampled": "logging.googleapis.com/trace_sampled",
        },
        timestamp=True,
        datefmt="%Y-%m-%dT%H:%M:%SZ",
    )
    handler.setFormatter(formatter)

    return handler
