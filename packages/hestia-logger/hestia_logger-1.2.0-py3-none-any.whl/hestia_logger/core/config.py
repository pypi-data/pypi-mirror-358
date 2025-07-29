"""
HESTIA Logger - Configuration Module.

Defines environment-based logging settings for HESTIA Logger.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import os
import socket
import logging
from dotenv import load_dotenv

# Load environment variables from `.env` file, but ignore errors in test environments
try:
    load_dotenv()
except Exception:
    pass


# Detect runtime environment (local or container)
def detect_container():
    """Detects if running inside a container environment."""
    try:
        return (
            os.path.exists("/.dockerenv") or "docker" in open("/proc/1/cgroup").read()
        )
    except FileNotFoundError:
        return False


def is_running_in_container():
    override = os.getenv("IS_CONTAINER_OVERRIDE")
    if override is not None:
        return override.lower() == "true"
    return detect_container()


IS_CONTAINER = is_running_in_container()

# Configuration values
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

ENVIRONMENT = os.getenv("ENVIRONMENT", "local").lower()
IS_CONTAINER = detect_container()

# Retrieve system identifiers
HOSTNAME = socket.gethostname()
CONTAINER_ID = (
    open("/proc/self/cgroup").read().splitlines()[-1].split("/")[-1]
    if IS_CONTAINER and os.path.exists("/proc/self/cgroup")
    else "N/A"
)

# Ensure log directory exists
LOGS_DIR = os.getenv(
    "LOGS_DIR",
    "/var/logs" if IS_CONTAINER else os.path.join(os.getcwd(), "logs"),
)

try:
    os.makedirs(LOGS_DIR, exist_ok=True)
except PermissionError:
    # Silently ignore if we lack permissions
    pass

LOG_FILE_PATH_APP = os.path.join(LOGS_DIR, "app.log")
LOG_FILE_PATH_INTERNAL = os.path.join(LOGS_DIR, "hestia_logger_internal.log")

# Safe Conversion of `LOG_LEVEL`
LOG_LEVEL_STR = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
LOG_LEVEL = LOG_LEVELS.get(LOG_LEVEL_STR, logging.INFO)

# Read Elasticsearch host if provided
ELASTICSEARCH_HOST = os.getenv("ELASTICSEARCH_HOST", "").strip()

# Enable or Disable Internal Logging
ENABLE_INTERNAL_LOGGER = os.getenv("ENABLE_INTERNAL_LOGGER", "false").lower() == "true"

# Log Rotation Settings
LOG_ROTATION_TYPE = os.getenv("LOG_ROTATION_TYPE", "size")
LOG_ROTATION_WHEN = os.getenv("LOG_ROTATION_WHEN", "midnight")
LOG_ROTATION_INTERVAL = int(os.getenv("LOG_ROTATION_INTERVAL", 1))
LOG_ROTATION_BACKUP_COUNT = int(os.getenv("LOG_ROTATION_BACKUP_COUNT", 5))
LOG_ROTATION_MAX_BYTES = int(os.getenv("LOG_ROTATION_MAX_BYTES", 10 * 1024 * 1024))
