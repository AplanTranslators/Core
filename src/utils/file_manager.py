import difflib
import json
from logging import Logger
import shutil
from pathlib import Path
from typing import Dict, List, Optional

from ..logger.logger import Logger
from ..singleton.singleton import SingletonMeta

ExampleEntry = Dict[str, str]


class FilesMngr(metaclass=SingletonMeta):
    def __init__(self):
        self.logger: Logger = Logger(self.__class__.__qualname__)

    def isPathExist(self, path: Path):
        if not path.exists():
            raise ValueError(f"Path '{path}' does not exist")

    def isTestingFile(self, path: Path, language_type: str):
        self.isPathExist(path)

        if path.is_file() and path.suffix == f".{language_type}":
            return True
        else:
            raise ValueError(f"Path '{path}' is not a .{language_type} file")

    def compare(self, file1_path: Path, file2_path: Path) -> list:
        with open(file1_path, "r", encoding="utf-8") as file1, open(
            file2_path, "r", encoding="utf-8"
        ) as file2:
            file1_lines = file1.readlines()
            file2_lines = file2.readlines()

        diff = difflib.unified_diff(
            file1_lines,
            file2_lines,
            fromfile=str(file1_path),
            tofile=str(file2_path),
            lineterm="",
        )
        differences = list(diff)

        return differences

    def compareAplanByPathes(
        self,
        path1: Path,
        path2: Path,
        extensions_to_compare: Optional[List[str]] = None,
    ) -> bool:
        result = False
        if extensions_to_compare is None:
            extensions_to_compare = [".act", ".behp", ".env_descript", ".evt_descript"]

        for ext in extensions_to_compare:
            # Використовуємо rglob для рекурсивного пошуку або glob для поточного каталогу
            files1 = list(path1.glob(f"*{ext}"))
            files2 = list(path2.glob(f"*{ext}"))

            for file1 in files1:
                filename = file1.name
                file2 = path2 / filename
                if file2 in files2:
                    differences = self.compare(file1, file2)
                    if differences:
                        self.logger.error(f"File {filename} differences:")
                        for diff in differences:
                            self.logger.error(f"{diff}")
                        result = True
                    else:
                        self.logger.info(
                            f"Files {filename} are the same ", color="blue"
                        )
                else:
                    self.logger.error(f"File {filename} not found in {path2}")

        return result

    def removeDirectory(self, directory_path: Path):
        if directory_path.exists() and directory_path.is_dir():
            shutil.rmtree(directory_path)
            self.logger.info(
                f"Directory {directory_path} has been removed.\n", color="bold_yellow"
            )
        else:
            self.logger.warning(f"Directory {directory_path} does not exist.\n")

    def loadExamplesFromJson(self, filepath: Path) -> List[ExampleEntry]:
        if not filepath.exists():
            self.logger.warning(
                f"JSON file not found at '{filepath}'. Returning empty list."
            )
            return []

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise TypeError("JSON file should contain a list of example objects.")

        return data

    def replaceFilename(self, path: Path, new_filename: str) -> Path:
        """The function `replaceFilename` takes a file path and a new filename, and returns a new path with
        the updated filename.

        Parameters
        ----------
        path : Path
            The `path` parameter is a Path representing the file path of the original file including the
        filename.
        new_filename : str
            The `new_filename` parameter is a string that represents the new filename that you want to use for
        the file in the given `path`.

        Returns
        -------
            The function `replaceFilename` returns a new path with the updated filename.

        """
        return path.with_name(new_filename)
