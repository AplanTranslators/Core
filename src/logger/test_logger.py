import logging
from pathlib import Path

from ..logger.logger import AplanLogger, LogAplanFileHandler, LogFileHandler, Logger


class TestLogger:
    def test_logger_activation(self, caplog):
        """Verify that the logger is activated and deactivated correctly."""
        log = Logger("test_activation")
        assert log.active is True
        log.deactivate()
        assert log.active is False
        log.info("This should not be logged")
        assert "This should not be logged" not in caplog.text
        log.activate()
        assert log.active is True
        log.info("This should be logged")
        assert "This should be logged" in caplog.text

    def test_log_messages(self, caplog):
        """Checks that the logger generates messages for all levels."""
        log = Logger("test_messages")
        with caplog.at_level(logging.DEBUG):
            log.debug("Debug message")
            log.info("Info message")
            log.warning("Warning message")
            log.error("Error message")
            log.critical("Critical message")

        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
        assert "Critical message" in caplog.text

    def test_log_with_color(self, caplog):
        """Checks that the `color` attribute is correctly added to the log entry."""
        log = Logger("test_color")
        with caplog.at_level(logging.INFO):
            log.info("Message with color", color="blue")

        record = caplog.records[0]
        assert "temp_log_color" in record.__dict__
        assert record.temp_log_color == "blue"

    def test_delimetr_logging(self, caplog):
        """Checks that the `delimetr` method correctly creates delimiters."""
        log = Logger("test_delimiter")
        with caplog.at_level(logging.INFO):
            log.delimetr(size=10, text="Test text")

        expected_delimiter = "=========="
        assert expected_delimiter in caplog.text
        assert "Test text" in caplog.text


class TestFileHandlers:
    def test_log_file_handler_creation(self, tmp_path: Path):
        """Verifies that the LogFileHandler creates a file with a correct name and timestamp."""
        file_path_str = str(tmp_path / "test_log.log")
        handler = LogFileHandler(file_path_str)

        files_in_dir = list(tmp_path.iterdir())
        assert len(files_in_dir) == 1

        file_name = files_in_dir[0].name
        assert file_name.startswith("test_log_")
        assert file_name.endswith(".log")

    def test_log_file_handler_writes(self, tmp_path: Path):
        """Checks that the LogFileHandler is correctly recording messages."""
        file_path_str = str(tmp_path / "test_write.log")
        handler = LogFileHandler(file_path_str)

        logger = logging.getLogger("test_file_write")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        logger.info("This should be in the file.")

        file_path = list(tmp_path.glob("*.log"))[0]
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "This should be in the file." in content

        logger.removeHandler(handler)

    def test_log_aplan_file_handler_creation(self, tmp_path: Path):
        """Verifies that LogAplanFileHandler creates a file at the specified path."""
        dir_path = tmp_path / "aplan_results"
        handler = LogAplanFileHandler(dir_path, "project.act")

        file_path = dir_path / "project.act"
        assert file_path.exists()
        assert file_path.is_file()

    def test_log_aplan_file_handler_writes(self, tmp_path: Path):
        """
        Verifies that the LogAplanFileHandler is recording messages.
        Please note: we are not using a filter here, we are just checking the entry.
        """
        dir_path = tmp_path / "aplan_results"
        handler = LogAplanFileHandler(dir_path, "test.behp")

        logger = logging.getLogger("test_aplan_write")
        logger.setLevel(logging.INFO)
        logger.addHandler(handler)

        logger.info("This is a BEHP message")

        file_path = dir_path / "test.behp"
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "This is a BEHP message" in content

        logger.removeHandler(handler)


class TestAplanLogger:
    def test_all_aplan_logger_functions(self, tmp_path: Path):
        """Перевіряє ініціалізацію, запис та режим push в одному тесті."""
        apl_logger = AplanLogger(tmp_path)

        # 1. Перевірка створення файлів
        assert (tmp_path / "project.env_descript").exists()
        assert (tmp_path / "project.evt_descript").exists()
        assert (tmp_path / "project.act").exists()
        assert (tmp_path / "project.behp").exists()

        # 2. Перевірка запису
        apl_logger.evt("Event log message")
        apl_logger.env("Environment log message")
        apl_logger.act("Action log message")
        apl_logger.behp("Behavior log message")

        with open(tmp_path / "project.evt_descript", "r", encoding="utf-8") as f:
            assert "Event log message" in f.read()
        # ... та інші перевірки ...

        # 3. Перевірка режиму push
        apl_logger.evtPush("Event without newline")
        apl_logger.evt("Event with newline")

        with open(tmp_path / "project.evt_descript", "r", encoding="utf-8") as f:
            content = f.read()
        assert "Event without newline" in content
        assert content.endswith("Event with newline\n")
