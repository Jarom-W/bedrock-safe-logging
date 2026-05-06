import json
import logging
import sys
from datetime import datetime, UTC
from typing import Any

from config import settings
from trace import get_trace_id


class TraceIdFilter(logging.Filter): # Filter logs by those that contain our trace id
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id()
        return True


class JsonFormatter(logging.Formatter): #Format logging messages into clean Json
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "trace_id": getattr(record, "trace_id", "-"),
            "message": record.getMessage(),
        }

        for attr in (
            "event",
            "model_id",
            "status",
            "latency_ms",
            "input_tokens",
            "output_tokens",
            "stop_reason",
            "error_type",
            "aws_profile",
            "aws_region",
            "prompt_logged",
            "prompt",
            "env",
            "estimated_cost_usd"
        ):
            value = getattr(record, attr, None)
            if value is not None:
                payload[attr] = value

        return json.dumps(payload)


def configure_logging() -> logging.Logger: #Building logger object
    logger = logging.getLogger("bedrock_cli")
    logger.setLevel(settings.log_level.upper())
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    handler.addFilter(TraceIdFilter())

    logger.addHandler(handler)
    logger.propagate = True
    return logger


logger = configure_logging()


def log_event(level: str, message: str, **fields: Any) -> None: #Execute the logging event
    extra = fields.copy()
    logger.log(getattr(logging, level.upper()), message, extra=extra)
