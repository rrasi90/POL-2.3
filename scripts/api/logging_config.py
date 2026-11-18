"""Structured access logging for the POL HTTP transport.

Only route path, method, status, duration, correlation ID and exception type
are recorded. Request bodies, query strings, authorization headers, OTPs and
phone numbers are deliberately excluded.
"""

from __future__ import annotations

import logging
import os

LOGGER_NAME = "pol.api.access"
_CONFIGURED = False


class KeyValueFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base = f"{record.levelname} {record.getMessage()}"
        extras = getattr(record, "fields", None)
        if extras:
            rendered = " ".join(f"{key}={value}" for key, value in extras.items())
            return f"{base} {rendered}"
        return base


def configure_logging() -> logging.Logger:
    global _CONFIGURED
    logger = logging.getLogger(LOGGER_NAME)
    if not _CONFIGURED:
        level_name = os.getenv("POL_LOG_LEVEL", "INFO").upper()
        logger.setLevel(getattr(logging, level_name, logging.INFO))
        root = logging.getLogger()
        # Let Uvicorn / pytest own the handler when one exists. Only install a
        # private stream handler in standalone execution with no root handler.
        if not root.handlers and not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(KeyValueFormatter())
            logger.addHandler(handler)
            logger.propagate = False
        else:
            logger.propagate = True
        _CONFIGURED = True
    return logger


def get_access_logger() -> logging.Logger:
    return configure_logging()
