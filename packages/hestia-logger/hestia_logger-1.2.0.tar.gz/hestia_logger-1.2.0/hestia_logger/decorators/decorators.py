import functools
import time
import sys
import asyncio
import json
import inspect
import traceback
import os
import re

from collections.abc import Mapping, Sequence
from hestia_logger.core.custom_logger import get_logger

# Keys that should be redacted
SENSITIVE_KEYS = {"password", "token", "secret", "apikey", "api_key", "credential"}

# Regex patterns for masking credentials in strings
RE_PARAM = re.compile(
    r"(?P<key>password|token|secret|apikey|api_key|credential)=(?P<val>[^&\s;]+)",
    re.IGNORECASE,
)

# capture://user:pass@ → group(1)="//user:", group(2)="pass", group(3)="@"
RE_URL_CRED = re.compile(r"(//[^:/]+:)([^@]+)(@)")


def mask_string(s: str) -> str:
    """
    Mask credential patterns in strings, including URL-embedded passwords
    and query-parameter secrets.
    """
    # Mask query-param style secrets (e.g. ?password=foo)
    s = RE_PARAM.sub(lambda m: f"{m.group('key')}=***", s)
    # Mask URL-embedded credentials (e.g. //user:pass@)
    s = RE_URL_CRED.sub(lambda m: f"{m.group(1)}***{m.group(3)}", s)
    return s


def deep_mask(obj):
    """
    Recursively traverse mappings, sequences, and strings to redact
    any sensitive values.
    """
    if isinstance(obj, Mapping):
        return {
            key: "***" if key.lower() in SENSITIVE_KEYS else deep_mask(value)
            for key, value in obj.items()
        }
    elif isinstance(obj, str):
        return mask_string(obj)
    elif isinstance(obj, Sequence) and not isinstance(obj, (str, bytes, bytearray)):
        # Handle lists, tuples, etc.
        return type(obj)(deep_mask(item) for item in obj)
    else:
        # For numbers, booleans, None, or unknown objects, leave as-is
        return obj


def safe_serialize(obj):
    """
    First applies deep_mask to redact secrets, then converts to JSON.
    Falls back to masked string if obj is not JSON-serializable.
    """
    masked = deep_mask(obj)
    try:
        return json.dumps(masked, ensure_ascii=False)
    except TypeError:
        return mask_string(str(masked))


def get_caller_script_name():
    """Returns the calling script's filename, ignoring pytest internals."""
    stack = inspect.stack()
    for frame in reversed(stack):
        script_path = frame.filename
        if "pytest" not in script_path:
            return os.path.basename(script_path).replace(".py", "")
    return "unknown_script"


def log_execution(func=None, *, logger_name=None):
    if func is None:
        return lambda f: log_execution(f, logger_name=logger_name)

    caller_script_name = get_caller_script_name()
    service_logger = get_logger(logger_name or caller_script_name)
    app_logger = get_logger("app", internal=True)

    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            sanitized_args = deep_mask(args)
            sanitized_kwargs = deep_mask(kwargs)

            log_entry = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime()),
                "service": service_logger.name,
                "function": func.__name__,
                "status": "started",
                "args": safe_serialize(sanitized_args),
                "kwargs": safe_serialize(sanitized_kwargs),
            }

            app_logger.info(json.dumps(log_entry, ensure_ascii=False))
            service_logger.info(f"📌 Started: {func.__name__}()")

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                log_entry.update(
                    {
                        "status": "completed",
                        "duration": f"{duration:.4f} sec",
                        # Mask the result as well
                        "result": safe_serialize(result),
                    }
                )

                app_logger.info(json.dumps(log_entry, ensure_ascii=False))
                service_logger.info(
                    f"✅ Finished: {func.__name__}() in {duration:.4f} sec"
                )
                return result

            except Exception as e:
                log_entry.update(
                    {
                        "status": "error",
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                    }
                )
                app_logger.error(json.dumps(log_entry, ensure_ascii=False))
                service_logger.error(f"❌ Error in {func.__name__}: {e}")
                raise

        return async_wrapper
    else:

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            sanitized_args = deep_mask(args)
            sanitized_kwargs = deep_mask(kwargs)

            log_entry = {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.Z", time.gmtime()),
                "service": service_logger.name,
                "function": func.__name__,
                "status": "started",
                "args": safe_serialize(sanitized_args),
                "kwargs": safe_serialize(sanitized_kwargs),
            }

            app_logger.info(json.dumps(log_entry, ensure_ascii=False))
            service_logger.info(f"📌 Started: {func.__name__}()")

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time

                log_entry.update(
                    {
                        "status": "completed",
                        "duration": f"{duration:.4f} sec",
                        # Mask the result as well
                        "result": safe_serialize(result),
                    }
                )

                app_logger.info(json.dumps(log_entry, ensure_ascii=False))
                service_logger.info(
                    f"✅ Finished: {func.__name__}() in {duration:.4f} sec"
                )
                return result

            except Exception as e:
                exc_type, exc_value, exc_tb = sys.exc_info()
                tb_summary = traceback.extract_tb(exc_tb)
                last_call = tb_summary[-1] if tb_summary else None

                error_location = {
                    "filename": last_call.filename if last_call else None,
                    "line": last_call.lineno if last_call else None,
                    "function": last_call.name if last_call else func.__name__,
                }

                log_entry.update(
                    {
                        "status": "error",
                        "error": str(e),
                        "traceback": traceback.format_exc(),
                        "location": error_location,
                    }
                )

                app_logger.error(json.dumps(log_entry, ensure_ascii=False))
                service_logger.error(
                    f"❌ Error in {error_location['function']} at {error_location['filename']}:{error_location['line']} – {e}"
                )
                raise

        return sync_wrapper
