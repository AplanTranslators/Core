import os
from pathlib import Path
import sys
import time
import traceback
from typing import Any, Callable
from dataclasses import dataclass, field
from ..translator.base_translator_mngr import BaseTranslationManager
from ..utils.file_manager import FilesMngr
from ..logger.logger import Logger
from ..program.program import Program
from ..utils.time import TimeUtils


@dataclass
class OperationResult:
    """Dataclass for storing the results of the operation."""

    success: bool
    message: str


@dataclass
class ExampleData:
    """Dataclass for data from the JSON example file."""

    file: Path
    result_dir: Path
    aplan_dir: Path


class BaseTool:
    # Константи для кольорів логування
    LOG_DELIMITER_MAIN = "cyan"
    LOG_DELIMITER_TEST = "purple"
    LOG_DELIMITER_ERROR = "bold_red"
    LOG_INFO_TIME = "green"
    LOG_INFO_SOURCE_FILE = "blue"

    def __init__(self, name: str = "Tool"):
        self.name = name
        self.logger: Logger = Logger(self.__class__.__qualname__)
        self._translation_mngr: BaseTranslationManager | None = None
        self.file_manager = FilesMngr()
        self.time_utils = TimeUtils()
        self._type = None

    def setType(self, i_type: str):
        """Sets the type for the translator."""
        self._type = i_type

    def setTranslationMngr(self, i_translator: BaseTranslationManager):
        """Sets the type for the translator."""
        self._translation_mngr = i_translator

    def _logTimeSummary(
        self, start_time: float, process_name: str, is_start_log: bool = False
    ):
        """Logs the start, end, and execution times of the process."""
        current_time = time.time()
        execution_time = current_time - start_time

        if is_start_log:
            self.logger.info(
                f"{process_name} start time: {self.time_utils.formatTime_h_m_s(start_time)}",
                color=self.LOG_INFO_TIME,
            )
        else:
            self.logger.info(
                f"{process_name} end time: {self.time_utils.formatTime_h_m_s(current_time)}",
                color=self.LOG_INFO_TIME,
            )
            self.logger.info(
                f"{process_name} execution time: {self.time_utils.formatTime_m_s(execution_time)}",
                color=self.LOG_INFO_TIME,
            )

    def _handle_exception(self, e: Exception, message: str):
        """Handles and logs exceptions."""
        self.logger.error(f"{message}\n{e}")
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

    def start(self, source_path: Path, result_path: Path) -> bool:
        """
        Starts the main file translation process.
        Returns True if an error occurred, False otherwise.
        """
        if not self._type:
            self.logger.error("Select a type for the translator.")
            return True

        if not self._translation_mngr:
            self.logger.error("Select a translation manager.")
            return True

        self.logger.delimetr(
            text=f"{self.name.upper()} START", color=self.LOG_DELIMITER_MAIN
        )
        start_time = time.time()

        try:
            # Змінено: ініціалізація Program всередині `start`
            program = Program(result_path)

            self.file_manager.isTestingFile(source_path, self._type.lower())

            self._translation_mngr.setup(source_path)
            self._translation_mngr.translate()
            program.generateAplan()

            return False  # Успішне виконання
        except Exception as e:
            self._handle_exception(e, "Program finished with an error:")
            return True  # Помилка
        finally:
            self.logger.delimetr(color=self.LOG_DELIMITER_MAIN)
            self._logTimeSummary(start_time, "Program")
            self.logger.delimetr(
                text=f"{self._type.upper()} {self.name.upper()} END",
                color=self.LOG_DELIMITER_MAIN,
            )

    def _executeSingleOperation(
        self,
        item_number: int,
        source_file: Path,
        result_path: Path,
        aplan_code_path: Path | None,
        op_type: str,
    ) -> bool:
        """Unified logic for launching a single operation."""
        self.logger.delimetr(
            text=f"{op_type} {item_number}", color=self.LOG_DELIMITER_TEST
        )
        self.logger.info(f"Source file: {source_file}", color=self.LOG_INFO_SOURCE_FILE)

        has_error = False
        op_start_time = time.time()

        try:
            self.logger.activate()
            has_error = self.start(source_file, result_path)
            self.logger.deactivate()

            if op_type == "TEST":
                if has_error:
                    self.logger.error(f"Test {item_number} finished with an error.")

                if aplan_code_path and self.file_manager.compareAplanByPathes(
                    aplan_code_path, result_path
                ):
                    self.logger.error(f"Test {item_number} found differences.")
                    has_error = True

        except Exception as e:
            self._handle_exception(e, f"{op_type} {item_number} finished with error.")
            has_error = True
        finally:
            if op_type == "TEST":
                self.file_manager.removeDirectory(result_path)

            self.logger.info(
                f"{op_type} {item_number} execution time: {self.time_utils.formatTime_m_s(time.time() - op_start_time)}",
                color=self.LOG_INFO_TIME,
            )
            self.logger.delimetr(color=self.LOG_DELIMITER_MAIN)

        return has_error

    def runTest(self, test_number: int, data: ExampleData) -> bool:
        """Runs one test."""
        return self._executeSingleOperation(
            test_number, data.file, data.result_dir, data.aplan_dir, "TEST"
        )

    def runGeneration(self, gen_number: int, data: ExampleData) -> bool:
        """Launches one generation."""
        return self._executeSingleOperation(
            gen_number, data.file, data.result_dir, None, "GENERATION"
        )

    def _executeExamplesLoop(
        self,
        examples_list_path: Path,
        process_func: Callable[[int, ExampleData], bool],
        process_name: str,
    ) -> int:
        """Unified logic for the loop from the example file."""
        all_examples = self.file_manager.loadExamplesFromJson(examples_list_path)
        failed_items = []

        # Перетворення списку словників у список об'єктів ExampleData
        examples = [ExampleData(**data) for data in all_examples]

        self.logger.delimetr(
            text=f"{process_name.upper()} START", color=self.LOG_DELIMITER_TEST
        )
        start_time = time.time()
        self._logTimeSummary(start_time, process_name, is_start_log=True)

        for item_number, data in enumerate(examples):
            if process_func(item_number + 1, data):
                failed_items.append((item_number + 1, data.file))

        self._logTimeSummary(start_time, process_name)

        if not failed_items:
            self.logger.delimetr(
                text=f"{process_name.upper()} SUCCESS", color=self.LOG_DELIMITER_TEST
            )
            return 0

        self.logger.delimetr(
            text=f"{process_name.upper()} FAILED", color=self.LOG_DELIMITER_ERROR
        )
        self.logger.critical(f"Errors in {process_name.lower()}: {failed_items}\n")
        return 1

    def testsStart(self, examples_list_path: Path) -> int:
        """Runs a series of tests based on a sample file."""
        return self._executeExamplesLoop(examples_list_path, self.runTest, "TESTS")

    def regenerationStart(
        self, examples_list_path: Path | None = None, path_to_file: Path | None = None
    ) -> int:
        """Starts the code generation process."""
        if not examples_list_path and not path_to_file:
            self.logger.error("Please input a path for regeneration.")
            return 1  # Використовуємо return замість sys.exit для кращого тестування

        if path_to_file:
            return self._runSingleFileRegeneration(path_to_file)

        return self._executeExamplesLoop(
            examples_list_path, self.runGeneration, "GENERATIONS"
        )

    def _runSingleFileRegeneration(self, path_to_file: Path) -> int:
        """Logic for generating a single file."""
        self.logger.delimetr(
            text="SINGLE GENERATION START", color=self.LOG_DELIMITER_TEST
        )
        start_time = time.time()
        self.logger.info(
            f"Generation process start time: {self.time_utils.formatTime_h_m_s(start_time)}",
            color=self.LOG_INFO_TIME,
        )

        source_file = path_to_file
        result_path = path_to_file.parent / "aplan"

        # Обгортаємо виклик, щоб він відповідав сигнатурі `runGeneration`
        data = ExampleData(file=source_file, result_dir=result_path, aplan_dir=None)
        has_error = self.runGeneration(1, data)

        self._logTimeSummary(start_time, "Single Generation Process")

        if has_error:
            self.logger.delimetr(
                text="SINGLE GENERATION FAILED", color=self.LOG_DELIMITER_ERROR
            )
            self.logger.critical(f"Errors in single generation: {source_file}")
            return 1
        else:
            self.logger.delimetr(
                text="SINGLE GENERATION SUCCESS", color=self.LOG_DELIMITER_TEST
            )
            return 0
