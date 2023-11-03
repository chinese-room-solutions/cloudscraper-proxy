"""Logger module for the application."""

import logging
import sys
from logging import Handler, LogRecord

import structlog


class StructlogHandler(Handler):
    def __init__(self):
        super().__init__()
        self.structlog = structlog.get_logger("flask")

    def emit(self, record: LogRecord):
        kwargs = record.__dict__.copy()
        kwargs.pop("msg", None)
        kwargs.pop("message", None)
        self.structlog.log(record.levelno, record.getMessage(), **kwargs)


class StructLoggerFactory(structlog.stdlib.LoggerFactory):
    def __init__(self, log_level: int):
        super().__init__()
        self.log_level = log_level

    def __call__(self, *args: any) -> logging.Logger:
        logger = super().__call__(*args)
        logger.setLevel(self.log_level)
        return logger


def setup_logging(filename: str, log_level: int = logging.INFO, dev: bool = False):
    """Setup the global logging configuration.

    Args:
        log_level (int, optional): The log level. Defaults to logging.INFO.
        filename (str, optional): The log file name. If not specified, log writes to stdout.
        dev (bool, optional): Whether to use the pretty development renderer or not.
            Use with console output. Defaults to False.
    """

    if filename is None:
        handler = logging.StreamHandler(sys.stdout)
    else:
        handler = logging.FileHandler(filename)

    root_logger = logging.getLogger()
    if not root_logger.hasHandlers():
        root_logger.addHandler(handler)

    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    if dev:
        processors.append(structlog.dev.ConsoleRenderer(colors=True, sort_keys=False))
    else:
        processors.append(structlog.processors.JSONRenderer())

    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=StructLoggerFactory(log_level),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
