"""
HESTIA Logger - Console Handler.

Defines a structured console handler that outputs logs to the terminal
with proper formatting, including optional colored logs for better visibility.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import logging
import colorlog  # Provides colored console output

__all__ = ["console_handler"]

# Create console handler with a colorized formatter
formatter = colorlog.ColoredFormatter(
    "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)
