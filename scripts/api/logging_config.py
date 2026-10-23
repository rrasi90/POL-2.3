"""Structured access logging for the POL HTTP transport (TODO-086).

Log lines are single-line key=value records so they stay greppable and never
carry request bodies, authorization headers, OTP codes or phone numbers.
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
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(KeyValueFormatter())
            logger.addHandler(handler)
        logger.propagate = False
        _CONFIGURED = True
    return logger


def get_access_logger() -> logging.Logger:
    return configure_logging()
