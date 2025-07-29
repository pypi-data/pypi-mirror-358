from .logger import Logger, shutdown_loggers, LOGGERS_STORAGE
from .enums import Levels, LogFormats
from .formatters import LogFormatter
from .handlers import FolderHandler
from .dto import FormatterDTO, FolderHandlerDTO
from .types import AsyncLogger

__all__ = [
    # Enums
    "Levels",
    "LogFormats",

    # Main classes
    "Logger",
    "LogFormatter",
    "FolderHandler",

    # Functions
    "shutdown_loggers",

    # Internals (optional)
    "LOGGERS_STORAGE",
    "FormatterDTO",
    "FolderHandlerDTO",
    "AsyncLogger"
]

__version__ = "0.2.2"  # Access to version
