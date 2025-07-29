"""Logging utilities for the RiskGPT package."""

from __future__ import annotations

import logging
from typing import Optional

# Package-wide logger
logger = logging.getLogger("src")
logger.addHandler(logging.NullHandler())


def configure_logging(
    level: int = logging.INFO, handler: Optional[logging.Handler] = None
) -> logging.Logger:
    """Configure logging for RiskGPT.

    Parameters
    ----------
    level:
        Logging level for the RiskGPT logger. Defaults to ``logging.INFO``.
    handler:
        Optional custom handler. If not provided, a ``StreamHandler`` with a
        basic format is used.
    """
    if handler is None:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        handler.setFormatter(formatter)

    # Avoid adding duplicate handlers when called multiple times
    if handler not in logger.handlers:
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger
