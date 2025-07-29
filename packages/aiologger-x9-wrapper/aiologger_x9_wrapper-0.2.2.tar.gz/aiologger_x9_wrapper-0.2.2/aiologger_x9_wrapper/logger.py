from datetime import datetime
from logging import DEBUG
from pathlib import Path
from typing import Dict, Optional

from aiologger import Logger as AioLogger  # type: ignore
from aiologger.handlers.files import AsyncFileHandler  # type: ignore
from aiologger.formatters.base import Formatter as AiologgerFormatter  # type: ignore

from aiologger_x9_wrapper.enums import Levels
from aiologger_x9_wrapper.formatters import LogFormatter
from aiologger_x9_wrapper.handlers import FolderHandler
from aiologger_x9_wrapper.dto import FormatterDTO, FolderHandlerDTO
from .types import AsyncLogger

LOGGERS_STORAGE: Dict[str, AsyncLogger] = {}  # Dictionary for storing loggers by dates


class Logger:
    def __init__(
            self,
            log_formatter: LogFormatter,
            folder_handler: FolderHandler,
            loggers_storage: Optional[Dict[str, AsyncLogger]] = None,
    ) -> None:
        """Necessary logger configuration for recording logs

        Args:
            log_formatter (LogFormatter): Log recording format

            folder_handler (FileHandler): Configuration for creating a folder

            loggers_storage (Dict[str, AioLogger]): Logger storage used
        """
        self._log_format: FormatterDTO = log_formatter.build_format()
        self._file_handler: FolderHandlerDTO = folder_handler.build_format()
        self.__loggers_storage: Dict[
            str, AsyncLogger
        ] = loggers_storage if loggers_storage is not None else LOGGERS_STORAGE

        self.__folder: Path = self.__create_folder()

    def __create_folder(self) -> Path:
        folder: Path = self._file_handler.folder_path / self._file_handler.folder_name  # type: ignore[operator]
        folder.mkdir(mode=0o755, exist_ok=True)

        return folder

    async def write_log(self, log_level: Levels, message: str, logger_name: str = "SERVICE") -> None:
        formatter: AiologgerFormatter = AiologgerFormatter(
            fmt=self._log_format.log_format,
            datefmt=self._log_format.datetime_format
        )

        current_date: str = datetime.now().strftime("%d.%m.%Y")
        log_filename: Path = self.__folder / f"{current_date}.log"  # type: ignore[operator]

        old_loggers = [date for date in self.__loggers_storage if date != current_date]  # Closing loggers for old dates
        for logger in old_loggers:
            old_logger = self.__loggers_storage.pop(logger)

            await old_logger.shutdown()

        if current_date not in self.__loggers_storage:  # Initializing a new logger for the current date
            custom_logger = AioLogger(name=logger_name)

            file_handler = AsyncFileHandler(  # Setting up a file handler
                filename=str(log_filename),
                mode="a",
                encoding="utf-8",
            )
            file_handler.formatter = formatter
            file_handler.level = DEBUG  # Minimum logging level

            custom_logger.add_handler(file_handler)
            self.__loggers_storage[current_date] = custom_logger

        else:
            custom_logger = self.__loggers_storage[current_date]

        match log_level.value:
            case "DEBUG":
                await custom_logger.debug(message)
            case "INFO":
                await custom_logger.info(message)
            case "WARNING":
                await custom_logger.warning(message)
            case "ERROR":
                await custom_logger.error(message)
            case "CRITICAL":
                await custom_logger.critical(message)


async def shutdown_loggers(loggers_storage: Optional[Dict[str, AsyncLogger]] = None) -> None:
    if loggers_storage is None:
        loggers_storage = LOGGERS_STORAGE

    for date in list(loggers_storage.keys()):
        logger: AsyncLogger = loggers_storage.get(date)  # type: ignore

        if logger:
            await logger.shutdown()
            del loggers_storage[date]
