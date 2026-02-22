"""
Structured JSON logging configuration.

Call setup_logging() once at startup to configure all loggers
to emit structured JSON lines to stderr.
"""

import logging
import sys

from pythonjsonlogger import json as json_logger


def setup_logging(level: str = "INFO") -> None:
    """Configure the root logger to output structured JSON."""
    handler = logging.StreamHandler(sys.stderr)
    formatter = json_logger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={"asctime": "timestamp", "levelname": "level", "name": "module"},
    )
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
