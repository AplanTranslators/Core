import os
from pathlib import Path
import sys
import time
import traceback
from ..translator.base_translator_mngr import BaseTranslationManager
from ..utils.file_manager import FilesMngr
from ..logger.logger import Logger
from ..program.program import Program
from ..utils.time import TimeUtils


class BaseTool:
    # --- Конфігурація логування та повідомлень ---
    time_utils = TimeUtils()
    file_manager = FilesMngr()
    name = ""
    _type = None

    # Константи для кольорів логування
    LOG_DELIMITER_COLOR_MAIN = "cyan"
    LOG_DELIMITER_COLOR_TEST = "purple"
    LOG_DELIMITER_COLOR_ERROR = "bold_red"
    LOG_INFO_COLOR_TIME = "green"
    LOG_INFO_COLOR_SOURCE_FILE = "blue"

    # Константи для повідомлень
    MSG_TOOL_START = "{tool_name} START"
    MSG_MAIN_PROGRAM = "MAIN PROGRAM"
    MSG_PROGRAM_START_TIME = "Program start time: {time_str}"
    MSG_PROGRAM_END_TIME = "Program end time: {time_str}"
    MSG_PROGRAM_EXECUTION_TIME = "Program execution time: {time_str}"
    MSG_PROGRAM_ERROR = "Program finished with error: \n"
    MSG_TOOL_END = "{tool_type} {tool_name} END"

    MSG_SOURCE_FILE = "Source file : {file_path}"

    MSG_TEST_START_DELIMITER = "TEST {test_number}"
    MSG_TEST_ERROR_FINISHED = "Test {test_number} finished with error: "
    MSG_TEST_ERROR_DIFFERENCES = "Test {test_number} found differences."
    MSG_TEST_EXECUTION_TIME = "Test {test_number} execution time: {time_str}"
    MSG_TESTS_START_DELIMITER = "TESTS START"
    MSG_TESTING_START_TIME = "Testing start time: {time_str}"
    MSG_TESTING_END_TIME = "Testing end time: {time_str}"
    MSG_TESTING_EXECUTION_TIME = "Testing execution time: {time_str}"
    MSG_TESTS_SUCCESS = "TESTS SUCCESS"
    MSG_TESTS_FAILED = "TESTS FAILED"
    MSG_ERRORS_IN_TESTS = "Errors in tests: {failed_list}"

    MSG_GENERATION_START_DELIMITER = "GENERATION {gen_number}"
    MSG_GENERATION_ERROR = "Generation {gen_number} finished with error:"
    MSG_GENERATION_EXECUTION_TIME = "Generation execution time: {time_str}"
    MSG_GENERATIONS_START_DELIMITER = "GENERATION START"
    MSG_GENERATION_PROCESS_START_TIME = "Generation process start time: {time_str}"
    MSG_GENERATION_PROCESS_END_TIME = "Generation process end time: {time_str}"
    MSG_GENERATION_PROCESS_EXECUTION_TIME = (
        "Generation process execution time: {time_str}"
    )
    MSG_GENERATION_SUCCESS = "GENERATION SUCCESS"
    MSG_GENERATION_FAILED = "GENERATION FAILED"
    MSG_ERRORS_IN_GENERATIONS = "Errors in generations: {failed_list}"

    MSG_SINGLE_GENERATION_START = "SINGLE GENERATION START"
    MSG_SINGLE_GENERATION_FAILED = "SINGLE GENERATION FAILED"
    MSG_SINGLE_GENERATION_SUCCESS = "SINGLE GENERATION SUCCESS"
    MSG_ERRORS_IN_SINGLE_GENERATION = "Errors in single generation: {file_path}"

    def __init__(self, name: str = "Tool"):
        self.name = name
        self.logger: Logger = Logger(self.__class__.__qualname__)
        self.translation_mngr = BaseTranslationManager()

    def setType(self, i_type: str):
        """Встановлює тип для транслятора."""
        self._type = i_type

    def _log_time_summary(
        self, start_time: float, process_name: str, is_start_log: bool = False
    ):
        """Допоміжний метод для логування часу початку, кінця та виконання процесу."""
        current_time = time.time()
        execution_time = current_time - start_time

        if is_start_log:
            self.logger.info(
                f"{process_name} start time: {self.time_utils.format_time_h_m_s(start_time)}",
                color=self.LOG_INFO_COLOR_TIME,
            )
        else:
            self.logger.info(
                f"{process_name} end time: {self.time_utils.format_time_m_s(current_time)}",
                color=self.LOG_INFO_COLOR_TIME,
            )
            self.logger.info(
                f"{process_name} execution time: {self.time_utils.format_time_date_h_m_s(execution_time)}",
                color=self.LOG_INFO_COLOR_TIME,
            )

    def _handle_exception(self, e: Exception, message: str):
        """Допоміжний метод для обробки винятків та логування."""
        self.logger.error(message)
        traceback.print_exception(type(e), e, e.__traceback__, file=sys.stderr)

    def start(self, path: str | None, result_path: str | None) -> bool:
        """
        Запускає основний процес перекладу файлу.
        Повертає True, якщо сталася помилка, інакше False.
        """

        if not self._type:
            self.logger.error("Select type for translator")
            return True  # Повертаємо True, оскільки це помилка

        self.logger.delimetr(
            text=self.MSG_TOOL_START.format(tool_name=self.name.upper()),
            color=self.LOG_DELIMITER_COLOR_MAIN,
        )
        start_time = time.time()
        self.logger.info(
            self.MSG_PROGRAM_START_TIME.format(
                time_str=self.time_utils.format_time_h_m_s(start_time)
            ),
            color=self.LOG_INFO_COLOR_TIME,
        )
        self.logger.delimetr(
            text=self.MSG_MAIN_PROGRAM,
            color=self.LOG_DELIMITER_COLOR_MAIN,
        )

        try:
            program = Program(result_path)

            if self.file_manager.isTestingFile(path, self._type.lower()):
                self.translation_mngr.setup(path)
                self.translation_mngr.translate()

            program.generateAplan()
            return False  # Успішне виконання
        except Exception as e:
            self._handle_exception(e, self.MSG_PROGRAM_ERROR)
            return True  # Помилка
        finally:
            self.logger.delimetr(color=self.LOG_DELIMITER_COLOR_MAIN)
            end_time = time.time()
            execution_time = end_time - start_time
            self.logger.info(
                self.MSG_PROGRAM_END_TIME.format(
                    time_str=self.time_utils.format_time_date_h_m_s(end_time)
                ),
                color=self.LOG_INFO_COLOR_TIME,
            )
            self.logger.info(
                self.MSG_PROGRAM_EXECUTION_TIME.format(
                    time_str=self.time_utils.format_time_m_s(execution_time)
                ),
                color=self.LOG_INFO_COLOR_TIME,
            )
            self.logger.delimetr(
                text=self.MSG_TOOL_END.format(
                    tool_type=self._type.upper(), tool_name=self.name.upper()
                ),
                color=self.LOG_DELIMITER_COLOR_MAIN,
            )

    def _execute_single_operation(
        self,
        operation_type: str,
        item_number: int,
        source_file: Path,
        result_path: Path,
        aplan_code_path: str = None,
    ) -> bool:
        """
        Уніфікована логіка для запуску однієї операції (тестування або генерації).
        Повертає True, якщо сталася помилка, інакше False.
        """
        has_error = False
        self.logger.delimetr(
            text=f"{operation_type.upper()} {item_number}",
            color=self.LOG_DELIMITER_COLOR_TEST,
        )
        op_start_time = time.time()

        try:
            self.logger.info(
                self.MSG_SOURCE_FILE.format(file_path=source_file),
                color=self.LOG_INFO_COLOR_SOURCE_FILE,
            )
            self.logger.activate()
            # Основна логіка: виклик start()

            has_error = self.start(source_file, result_path)
            self.logger.deactivate()

            if operation_type == "TEST":
                if has_error:
                    self.logger.error(
                        self.MSG_TEST_ERROR_FINISHED.format(test_number=item_number)
                    )

                differences_found = self.file_manager.compareAplanByPathes(
                    aplan_code_path, result_path
                )
                if differences_found:
                    self.logger.error(
                        self.MSG_TEST_ERROR_DIFFERENCES.format(test_number=item_number)
                    )
                    has_error = True

        except Exception as e:
            self._handle_exception(
                e, f"{operation_type} {item_number} finished with error:"
            )
            has_error = True
        finally:
            if operation_type == "TEST":
                self.file_manager.removeDirectory(result_path)

            op_execution_time = time.time() - op_start_time
            self.logger.info(
                f"{operation_type} {item_number} execution time: "
                + self.time_utils.format_time_date_h_m_s(op_execution_time),
                color=self.LOG_INFO_COLOR_TIME,
            )
            self.logger.delimetr(color=self.LOG_DELIMITER_COLOR_MAIN)

        return has_error

    def run_test(
        self,
        test_number: int,
        source_file: Path,
        result_path: Path,
        aplan_code_path: str,
    ) -> bool:
        """Запускає один тест."""
        return self._execute_single_operation(
            "TEST", test_number, source_file, result_path, aplan_code_path
        )

    def run_generation(
        self, gen_number: int, source_file: Path, result_path: Path
    ) -> bool:
        """Запускає одну генерацію."""
        return self._execute_single_operation(
            "GENERATION", gen_number, source_file, result_path, None
        )

    def _execute_examples_loop(
        self, examples_list_path: Path, process_func, process_name: str
    ) -> int:
        """
        Уніфікована логіка для запуску тестів або генерації з файлу прикладів.
        Повертає 0, якщо все успішно, 1, якщо є помилки.
        """
        all_examples = self.file_manager.loadExamplesFromJson(examples_list_path)
        failed_items = []

        self.logger.delimetr(
            text=f"{process_name.upper()} START",
            color=(
                self.LOG_DELIMITER_COLOR_TEST
                if process_name == "TESTS"
                else self.LOG_DELIMITER_COLOR_MAIN
            ),
        )
        start_time = time.time()
        self._log_time_summary(
            start_time, f"{process_name.capitalize()}", is_start_log=True
        )

        for item_number, data in enumerate(all_examples):
            # Передача всіх даних dict'ом до process_func для гнучкості
            if process_func(item_number + 1, data):
                failed_items.append((item_number + 1, data.get("file", "N/A")))

        self._log_time_summary(start_time, f"{process_name.capitalize()}")

        if not failed_items:
            self.logger.delimetr(
                text=f"{process_name.upper()} SUCCESS",
                color=self.LOG_DELIMITER_COLOR_TEST,
            )
            return 0
        else:
            self.logger.delimetr(
                text=f"{process_name.upper()} FAILED",
                color=self.LOG_DELIMITER_COLOR_ERROR,
            )
            self.logger.critical(f"Errors in {process_name.lower()}: {failed_items}\n")
            return 1

    def _run_single_test_wrapper(self, test_number: int, data: dict) -> bool:
        """Обгортка для run_test, щоб відповідати сигнатурі _execute_examples_loop."""
        source_file = data["file"]
        result_path = data["result_dir"]
        aplan_code_path = data["aplan_dir"]
        return self.run_test(test_number, source_file, result_path, aplan_code_path)

    def _run_single_generation_wrapper(self, gen_number: int, data: dict) -> bool:
        """Обгортка для run_generation, щоб відповідати сигнатурі _execute_examples_loop."""
        source_file = data["file"]
        result_path = data["aplan_dir"]  # У генерації aplan_dir є результатом
        return self.run_generation(gen_number, source_file, result_path)

    def tests_start(self, examples_list_path: str) -> int:
        """Запускає серію тестів на основі файлу прикладів."""
        return self._execute_examples_loop(
            examples_list_path, self._run_single_test_wrapper, "TESTS"
        )

    def regeneration_start(
        self, examples_list_path: Path = None, path_to_file: Path = None
    ) -> int:
        """
        Запускає процес генерації коду: або для всіх прикладів з файлу, або для одного SV-файлу.
        Повертає 0, якщо все успішно, 1, якщо є помилки.
        """
        if not examples_list_path and not path_to_file:
            self.logger.error("Please input path for regeneration.")
            sys.exit(1)

        if path_to_file is None:
            return self._execute_examples_loop(
                examples_list_path, self._run_single_generation_wrapper, "GENERATION"
            )
        else:

            # Обробка одного файлу окремо, оскільки він не зчитується з JSON-списку
            directory = os.path.dirname(path_to_file)
            source_file = path_to_file
            result_path = os.path.join(
                directory, "aplan"
            )  # Або інший шлях за замовчуванням для одного файлу

            self.logger.delimetr(
                text=self.MSG_SINGLE_GENERATION_START,
                color=self.LOG_DELIMITER_COLOR_TEST,
            )
            start_time = time.time()
            self.logger.info(
                self.MSG_GENERATION_PROCESS_START_TIME.format(
                    time_str=self.time_utils.format_time_h_m_s(start_time)
                ),
                color=self.LOG_INFO_COLOR_TIME,
            )

            has_error = self.run_generation(
                1, source_file, result_path
            )  # Для одного файлу використовуємо номер 1

            self._log_time_summary(start_time, "Single Generation Process")

            if has_error:
                self.logger.delimetr(
                    self.MSG_SINGLE_GENERATION_FAILED,
                    color=self.LOG_DELIMITER_COLOR_ERROR,
                )
                self.logger.critical(
                    self.MSG_ERRORS_IN_SINGLE_GENERATION.format(file_path=source_file)
                )
                return 1
            else:
                self.logger.delimetr(
                    self.MSG_SINGLE_GENERATION_SUCCESS,
                    color=self.LOG_DELIMITER_COLOR_TEST,
                )
                return 0
