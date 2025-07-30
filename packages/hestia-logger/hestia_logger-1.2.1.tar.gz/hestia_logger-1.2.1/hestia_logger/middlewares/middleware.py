"""
HESTIA Logger - Logging Middleware.

Provides middleware functions for logging request and response details
in web applications using FastAPI, Flask, and other frameworks. Enhanced with structured request ID support.

Author: FOX Techniques <ali.nabbi@fox-techniques.com>
"""

import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

import logging
import os
from ..handlers.console_handler import console_handler  # Use global console handler
from ..core.custom_logger import JSONFormatter  # Use JSON formatter

__all__ = ["LoggingMiddleware"]


class LoggingMiddleware:
    """
    Middleware that logs incoming requests and outgoing responses.
    """

    def __init__(self, logger_name="hestia_middleware"):
        """
        Initializes the middleware with a logger instance.
        """
        self.logger = logging.getLogger(logger_name)

        # Load log level from environment variable
        LOG_LEVELS = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        LOG_LEVEL_STR = os.getenv("MIDDLEWARE_LOG_LEVEL", "INFO").upper()
        LOG_LEVEL = LOG_LEVELS.get(LOG_LEVEL_STR, logging.INFO)
        self.logger.setLevel(LOG_LEVEL)

        # Use global console handler
        self.logger.addHandler(console_handler)

        # Use JSON formatting for structured logging
        json_formatter = JSONFormatter()
        file_handler = logging.FileHandler("logs/middleware.log")
        file_handler.setFormatter(json_formatter)
        self.logger.addHandler(file_handler)

        # Prevent log duplication
        self.logger.propagate = False

    def log_request(self, request):
        """
        Logs details of an incoming HTTP request.
        """
        log_entry = {
            "event": "incoming_request",
            "method": request.method,
            "url": str(request.url),
        }
        self.logger.info(log_entry)

        def log_request(self, request: Request):
            request_id = getattr(request.state, "request_id", "unknown")
            log_entry = {
                "event": "incoming_request",
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
                "query": str(request.url.query),
                "client": request.client.host if request.client else "unknown",
                "headers": {
                    "user-agent": request.headers.get("user-agent"),
                    "host": request.headers.get("host"),
                },
            }
            self.logger.info(log_entry)

    def log_response(self, request: Request, response: Response):
        """
        Logs details of an outgoing HTTP response.
        """
        request_id = getattr(request.state, "request_id", "unknown")
        log_entry = {
            "event": "outgoing_response",
            "request_id": request_id,
            "status_code": response.status_code,
        }
        self.logger.info(log_entry)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to inject a UUID-based request_id into the request state and response headers.
    """

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def setup_logging_middleware(app, logger_name="hestia_middleware"):
    """
    Apply HESTIA logging and request ID middleware to a FastAPI app.
    """
    logger = LoggingMiddleware(logger_name)

    @app.middleware("http")
    async def log_wrapper(request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        logger.log_request(request)
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.log_response(request, response)
        return response
