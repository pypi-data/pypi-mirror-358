"""
HESTIA Logger - Formatters Module.

Defines structured logging formatters for consistency across the logging system.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import json
import logging
from ..core.config import ENVIRONMENT, HOSTNAME, APP_VERSION


class JSONFormatter(logging.Formatter):
    def format(self, record):
        # If the original message is a dict, use it; otherwise, try parsing or wrap it as a plain message.
        if isinstance(record.msg, dict):
            message_content = record.msg
        else:
            try:
                parsed = json.loads(record.getMessage())
                message_content = (
                    parsed
                    if isinstance(parsed, dict)
                    else {"message": record.getMessage()}
                )
            except (json.JSONDecodeError, TypeError):
                message_content = {"message": record.getMessage()}

        # Base log entry
        log_entry = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S.%fZ")[:-3] + "Z",
            "level": record.levelname,
            "service": record.name,
            # Standardized metadata
            "environment": ENVIRONMENT,
            "hostname": HOSTNAME,
            "app_version": APP_VERSION,
        }

        # Merge any additional metadata from the LoggerAdapter (if present)
        if hasattr(record, "metadata"):
            if isinstance(record.metadata, dict):
                log_entry.update(record.metadata)
        # Merge the message content into the log entry for a flat structure.
        log_entry.update(message_content)
        return json.dumps(log_entry, ensure_ascii=False)
