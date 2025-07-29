from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FormatterDTO:
    log_format: Optional[str] = None
    datetime_format: Optional[str] = None


@dataclass
class FolderHandlerDTO:
    folder_path: Optional[Path] = None
    folder_name: Optional[Path] = None
