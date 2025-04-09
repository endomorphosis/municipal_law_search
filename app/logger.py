"""
Logging configuration module for the American Law Search application.

This module sets up the logging system with custom formatting and uses the
configuration from configs.py to determine the logging level. The logger created
here is used throughout the application for consistent logging behavior.

The log format includes timestamp, log level, filename, line number and message,
providing comprehensive context for each log entry.
"""
import logging


from configs import configs


_LEVEL = configs.LOG_LEVEL or logging.DEBUG # Default to DEBUG if not set in configs

# Configure logging
logging.basicConfig(level=_LEVEL, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
logger = logging.getLogger(__name__)