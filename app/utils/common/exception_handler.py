import logging
import sys


from app import configs


def exception_handler(exception_type, exception, traceback, debug_hook=sys.excepthook):
    """Handle exceptions based on the configured log level.

    This function provides a custom exception handler that either prints a simplified error
    message or calls the default exception hook based on the log level.

    Args:
        exception_type: The type of the raised exception.
        exception: The exception instance that was raised.
        traceback: The traceback object.
        debug_hook: The original exception hook to use when in debug mode. Defaults to sys.excepthook.

    Returns:
        None

    Note:
        If configs.LOG_LEVEL is set to logging.DEBUG, this will call the default exception
        handler with full traceback. Otherwise, it prints a simplified error message with
        the exception name and message.
    """
    if configs.LOG_LEVEL == logging.DEBUG:
        debug_hook(exception_type, exception, traceback)
    else:
        print(f"{exception_type.__name__}: {exception}")
