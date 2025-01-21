import logging
import json
import os
from logging.handlers import RotatingFileHandler
import sys

class VerceLLogger:
    def __init__(self, name='vercel_app'):
        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        # Clear any existing handlers to prevent duplicate logs
        self.logger.handlers.clear()

        # Create a handler that writes to stdout (Vercel's preferred logging method)
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.INFO)

        # JSON formatter for structured logging
        class JsonFormatter(logging.Formatter):
            def format(self, record):
                log_record = {
                    'timestamp': self.formatTime(record, self.datefmt),
                    'level': record.levelname,
                    'message': record.getMessage(),
                    'logger_name': record.name,
                    'environment': os.environ.get('VERCEL_ENV', 'development'),
                    'deployment_url': os.environ.get('VERCEL_URL', 'local')
                }
                return json.dumps(log_record)

        # Set JSON formatter
        stdout_handler.setFormatter(JsonFormatter())
        self.logger.addHandler(stdout_handler)

    def info(self, message, extra=None):
        """Log an info message"""
        extra = extra or {}
        self.logger.info(message, extra=extra)

    def warning(self, message, extra=None):
        """Log a warning message"""
        extra = extra or {}
        self.logger.warning(message, extra=extra)

    def error(self, message, exc_info=False, extra=None):
        """Log an error message"""
        extra = extra or {}
        self.logger.error(message, exc_info=exc_info, extra=extra)

    def debug(self, message, extra=None):
        """Log a debug message"""
        extra = extra or {}
        self.logger.debug(message, extra=extra)

