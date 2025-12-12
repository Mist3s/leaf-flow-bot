from __future__ import annotations

import logging
from logging.config import dictConfig


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(level: str = "INFO") -> None:
    dictConfig(
        {
            "version": 1,
            "formatters": {
                "default": {
                    "format": LOG_FORMAT,
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                    "level": level,
                }
            },
            "root": {
                "level": level,
                "handlers": ["console"],
            },
        }
    )
    logging.getLogger(__name__).debug("Logging configured", extra={"level": level})
