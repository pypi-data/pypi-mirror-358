from pathlib import Path

from aiologger_x9_wrapper.dto import FolderHandlerDTO


class FolderHandler:
    def __init__(
            self,
            path: str | Path,
            name: str | Path = "logs",
    ) -> None:
        """Configures file attributes.

        Args:
            path (str | Path): The path (or level) where the folder will be created.

            name (str | Path): The name given to the file.
        """
        self._name = name
        self._path = path

    def build_format(self) -> FolderHandlerDTO:
        result: FolderHandlerDTO = FolderHandlerDTO()

        result.folder_name = Path(self._name) if isinstance(self._name, str) else self._name
        result.folder_path = Path(self._path) if isinstance(self._path, str) else self._path

        return result
