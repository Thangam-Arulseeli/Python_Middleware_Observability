### Create app/core/logging_config.py
### We will use Python's built-in logging system and a JSON formatter.

import json
import logging
import sys

from datetime import datetime, timezone


class JsonFormatter(logging.Formatter):

    def format(self, record: logging.LogRecord) -> str:

        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        reserved_fields = {
            "name",
            "msg",
            "args",
            "levelname",
            "levelno",
            "pathname",
            "filename",
            "module",
            "exc_info",
            "exc_text",
            "stack_info",
            "lineno",
            "funcName",
            "created",
            "msecs",
            "relativeCreated",
            "thread",
            "threadName",
            "processName",
            "process",
            "taskName",
        }

        for key, value in record.__dict__.items():

            if key not in reserved_fields and not key.startswith("_"):
                try:
                    json.dumps(value)  # json.dumps() is a Python function that converts (serializes) a Python object into a JSON-formatted string.
                    log_data[key] = value

                except (TypeError, ValueError):
                    log_data[key] = repr(value)

        if record.exc_info:
            log_data["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps( # The function json.dumps() converts a Python object (such as a dictionary or list) into a JSON-formatted string (the s stands for "string")
            log_data,
            ensure_ascii=False,
            default=str,
        )


def setup_logging(log_level: str = "INFO") -> None:

    numeric_level = getattr(
        logging,
        log_level.upper(),
        None,
    )

    if not isinstance(numeric_level, int):
        raise ValueError(
            f"Invalid logging level: {log_level}"
        )

    handler = logging.StreamHandler(sys.stdout) # The line of code handler = logging.StreamHandler(sys.stdout) creates a logging handler that directs your program's log outputs explicitly to standard output (sys.stdout)

    handler.setFormatter(JsonFormatter())

    logging.basicConfig(
        level=numeric_level,
        handlers=[handler],
        force=True,
    )


'''
How does this work?
=========================
When the application executes:

logger.info(
    "Employee created",
    extra={
        "employee_id": 101,
        "department": "Engineering",
    },
)

The formatter produces a JSON record containing the message and additional fields.

For example:

{
  "timestamp": "2026-10-24T08:30:00+00:00",
  "level": "INFO",
  "logger": "app.services.employee_service",
  "message": "Employee created",
  "employee_id": 101,
  "department": "Engineering"
}

The timestamp is illustrative.


Why use extra?
==============
The extra parameter attaches additional attributes to the log record.

This:

logger.info(
    "Employee created",
    extra={"employee_id": 101},
)

is better for structured logging than embedding everything in a message:

logger.info(
    f"Employee {101} created"
)

The first form makes employee_id a distinct field that can be filtered or aggregated.

Production note: The formatter above is a minimal teaching implementation. For a larger application, consider a maintained structured-logging library, standardized OpenTelemetry fields, log rotation when writing to files, centralized collection, and appropriate exception redaction.

Never log passwords, access tokens, session cookies, or sensitive employee information.

'''