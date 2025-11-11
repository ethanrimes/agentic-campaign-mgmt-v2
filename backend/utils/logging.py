# backend/utils/logging.py

"""
Logging configuration for the social media agent framework.
Provides structured logging with consistent formatting.
"""

import logging
import sys
from typing import Optional
from pathlib import Path
import structlog
from backend.config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
                   If None, uses settings.log_level.

    This sets up:
    - Structured logging with structlog
    - Consistent timestamp formatting
    - Key-value pair formatting for easy parsing
    - Console output with colors (when terminal supports it)
    """
    level = log_level or settings.log_level

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.dev.ConsoleRenderer()
            if sys.stderr.isatty()
            else structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, level.upper()),
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a logger instance for the given module.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger

    Example:
        ```python
        from backend.utils import get_logger

        logger = get_logger(__name__)
        logger.info("Starting process", task_id="abc123", status="running")
        ```
    """
    return structlog.get_logger(name)
