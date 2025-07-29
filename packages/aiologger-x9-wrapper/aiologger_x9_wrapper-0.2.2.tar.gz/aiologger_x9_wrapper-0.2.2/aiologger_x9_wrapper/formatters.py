from typing import Tuple

from aiologger_x9_wrapper.enums import LogFormats
from aiologger_x9_wrapper.dto import FormatterDTO


class LogFormatter:
    def __init__(
            self,
            log_format: Tuple[LogFormats, ...] = (
                LogFormats.TIME, LogFormats.NAME, LogFormats.LEVEL, LogFormats.MESSAGE
            ),
            separator: str = " - ",
            datetime_format: str = "%d.%m.%Y %H:%M",
    ) -> None:
        """Configures the log output format

        Args:
            log_format (Tuple[LogFormats, ...]): The format you want to see the logs in. Example:
                log_format=(LogFormats.LEVEL, LogFormats.MESSAGE) -> LEVEL - MESSAGE

            separator (str): Separator between log attributes. Example:
                separator="___" -> LEVEL___MESSAGE

            datetime_format (str): Format of date and time output in logs. Example:
                datetime_format="%d.%m.%Y" -> 01.01.2001 - NAME - LEVEL - MESSAGE
        """
        self._log_format = log_format
        self._separator = separator
        self._datetime_format = datetime_format

    def build_format(self) -> FormatterDTO:
        result: FormatterDTO = FormatterDTO()

        result.log_format = self._separator.join(str(arg.value) for arg in self._log_format)
        result.datetime_format = self._datetime_format

        return result
