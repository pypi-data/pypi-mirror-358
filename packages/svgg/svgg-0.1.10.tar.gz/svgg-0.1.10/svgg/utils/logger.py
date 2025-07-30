"""Logging utilities for the SVGG package.

This module provides a centralized logging configuration for the SVGG package.
It sets up logging with configurable log levels and output formats.
"""

import logging
import sys
from pathlib import Path
from typing import Optional, Union


def setup_logger(
    name: str = "svgg",
    log_level: int = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
) -> logging.Logger:
    """Configure and return a logger with the specified settings.

    Args:
        name: Name of the logger. Defaults to 'svgg'.
        log_level: Logging level (e.g., logging.INFO, logging.DEBUG).
        log_file: Optional path to a log file. If not provided,
            logs to stderr.
        log_format: Format string for log messages.
        date_format: Format string for timestamps in log messages.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.handlers.clear()
    logger.setLevel(log_level)

    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    logger.propagate = False
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Get a logger with the specified name.

    This is a convenience function that returns a logger with default settings
    if it hasn't been configured yet.

    Args:
        name: Name of the logger. If None, returns the root logger.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name or "svgg")

    if not logger.handlers and not logging.getLogger().handlers:
        return setup_logger(name=name or "svgg")

    return logger
