"""Central logging configuration."""

import json
import logging
from datetime import UTC, datetime
from typing import Any

STANDARD_LOG_ATTRIBUTES = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "message",
    "module",
    "msecs",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
    "taskName",
}


class JsonFormatter(logging.Formatter):
    """Convert a LogRecord into a one-line JSON document."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            # "timestamp": datetime.now(timezone.utc).isoformat(),
            "timestamp": datetime.now(UTC),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        for key, value in record.__dict__.items():
            if key not in STANDARD_LOG_ATTRIBUTES and not key.startswith("_"):
                payload[key] = value

        if record.exc_info is not None:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, default=str)


def configure_logging() -> None:
    """Configure EASOP application loggers."""

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    for logger_name in ("easop", "easop.access"):
        application_logger = logging.getLogger(logger_name)
        application_logger.handlers.clear()
        application_logger.addHandler(handler)
        application_logger.setLevel(logging.INFO)
        application_logger.propagate = False
