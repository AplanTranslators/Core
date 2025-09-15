import os
import json
from pathlib import Path
import pytest
from unittest.mock import patch
from ..utils.file_manager import FilesMngr


@pytest.fixture
def file_manager():
    return FilesMngr()


# ---------------------------
# Tests for isPathExist
# ---------------------------
class TestIsPassExist:
    def test_existingPath(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Should pass when the file exists
        """
        path: Path = tmp_path / "file.txt"
        path.write_text("content")
        assert file_manager.isPathExist(path) is None

    def test_invalidPath(self, file_manager: FilesMngr):
        """
        Should raise ValueError when the path does not exist
        """
        path: Path = Path("/non/existent/path")
        with pytest.raises(ValueError, match="does not exist"):
            file_manager.isPathExist(path)


# ---------------------------
# Tests for isTestingFile
# ---------------------------
class TestIsTestingFile:
    def test_correctExtension(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Test that isTestingFile returns True for a valid file with the correct extension.
        """
        test_file = tmp_path / "test.py"
        test_file.touch()
        assert file_manager.isTestingFile(test_file, "py") is True

    def test_incorrectExtension(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Test that isTestingFile raises ValueError for a file with an incorrect extension.
        """
        test_file = tmp_path / "test.txt"
        test_file.touch()
        with pytest.raises(ValueError, match="is not a .py file"):
            file_manager.isTestingFile(test_file, "py")

    def test_pathIsDirectory(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Should raise ValueError when the path is a directory instead of a file
        """
        with pytest.raises(ValueError, match="is not a .py file"):
            file_manager.isTestingFile(tmp_path, "py")


# ---------------------------
# Tests for compare
# ---------------------------
class TestCompare:
    def test_identicalFiles(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Test that compare returns no differences for identical files.
        Identical files should return an empty diff
        """
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("same\ncontent\n")
        f2.write_text("same\ncontent\n")
        assert file_manager.compare(f1, f2) == []

    def test_differentFiles(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Test that compare returns differences for files with different content.
        Different files should show differences in diff output
        """
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("line1\n")
        f2.write_text("line2\n")
        diff = file_manager.compare(f1, f2)
        assert any("line1" in d or "line2" in d for d in diff)


class TestCompareEdgeCases:
    def test_emptyFiles(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Test that compare returns no differences for empty files.
        Empty files should return an empty diff"""
        f1 = tmp_path / "a.txt"
        f2 = tmp_path / "b.txt"
        f1.write_text("")
        f2.write_text("")
        assert file_manager.compare(f1, f2) == []

    def test_oneFileMissing(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Test that compare raises FileNotFoundError if one file is missing.
        If one file is missing, it should raise an error
        """
        f1: Path = tmp_path / "exists.txt"
        f1.write_text("content")
        f2: Path = tmp_path / "missing.txt"
        with pytest.raises(FileNotFoundError):
            file_manager.compare(f1, f2)


# ---------------------------
# Tests for compareAplanByPathes
# ---------------------------
class TestCompareAplanByPathes:
    def test_identicalFiles(self, file_manager: FilesMngr, tmp_path: Path, caplog):
        """
        Test that compareAplanByPathes returns no differences for identical files.
        Identical files should not log differences
        """
        dir1: Path = tmp_path / "dir1"
        dir2: Path = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        (dir1 / "test.act").write_text("same\n")
        (dir2 / "test.act").write_text("same\n")

        result = file_manager.compareAplanByPathes(dir1, dir2, [".act"])
        assert result is False
        assert "are the same" in caplog.text

    def test_differentFiles(self, file_manager: FilesMngr, tmp_path: Path, caplog):
        """
        Test that compareAplanByPathes logs differences for files with different content.
        Different files in directories should return True (differences found)
        """
        dir1: Path = tmp_path / "dir1"
        dir2: Path = tmp_path / "dir2"
        dir1.mkdir()
        dir2.mkdir()
        (dir1 / "test.act").write_text("aaa\n")
        (dir2 / "test.act").write_text("bbb\n")

        result = file_manager.compareAplanByPathes(dir1, dir2, [".act"])
        assert result is True
        assert "differences" in caplog.text


# ---------------------------
# Tests for remove_directory
# ---------------------------
class TestRemoveDirectory:
    def test_existingDirectory(self, file_manager: FilesMngr, tmp_path: Path, caplog):
        """
        Test that remove_directory removes an existing directory.
        Directory should be deleted if it exists
        """
        dir1: Path = tmp_path / "dir_to_remove"
        dir1.mkdir()
        file_manager.remove_directory(dir1)
        assert not dir1.exists()
        assert "has been removed" in caplog.text

    def test_missingDirectory(self, file_manager: FilesMngr, tmp_path: Path, caplog):
        """
        Test that remove_directory does nothing for a non-existing directory.
        If the directory does not exist, it should log a warning
        """
        dir1: Path = tmp_path / "non_existing"
        file_manager.remove_directory(dir1)
        assert "does not exist" in caplog.text

    def test_pathIsFile(self, file_manager: FilesMngr, tmp_path: Path, caplog):
        """
        Test that remove_directory raises an error if the path is a file.
        If the path is a file, it should log a warning and not delete anything
        """
        f: Path = tmp_path / "not_a_dir.txt"
        f.write_text("content")
        file_manager.remove_directory(f)
        assert "does not exist" in caplog.text


# ---------------------------
# Tests for load_examples_from_json
# ---------------------------
class TestLoadExamplesFromJson:
    def test_validJson(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Test that load_examples_from_json loads a valid JSON file.
        Should return a list of dictionaries from a valid JSON file
        """
        data = [{"a": "1"}, {"b": "2"}]
        f: Path = tmp_path / "examples.json"
        f.write_text(json.dumps(data))
        result = file_manager.load_examples_from_json(f)
        assert result == data

    def test_fileNotFound(self, file_manager: FilesMngr, tmp_path: Path, caplog):
        """
        Test that load_examples_from_json returns an empty list for a non-existing file.
        If the file does not exist, it should log a warning and return an empty list"""
        f: Path = tmp_path / "missing.json"
        result = file_manager.load_examples_from_json(f)
        assert result == []
        assert "not found" in caplog.text

    def test_invalidType(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Test that load_examples_from_json raises TypeError for invalid JSON format.
        If the JSON file does not contain a list, it should raise a TypeError
        """
        f: Path = tmp_path / "invalid.json"
        f.write_text(json.dumps({"not": "a list"}))
        with pytest.raises(TypeError):
            file_manager.load_examples_from_json(f)

    def test_invalidJsonFormat(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Test that load_examples_from_json raises JSONDecodeError for invalid JSON.
        If the JSON file is not valid, it should raise a JSONDecodeError
        """
        f: Path = tmp_path / "broken.json"
        f.write_text("{not valid json")
        with pytest.raises(json.JSONDecodeError):
            file_manager.load_examples_from_json(f)

    def test_emptyJsonList(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Test that load_examples_from_json returns an empty list for an empty JSON array.
        If the JSON file is an empty list, it should return an empty list
        """
        f: Path = tmp_path / "empty.json"
        f.write_text("[]")
        result = file_manager.load_examples_from_json(f)
        assert result == []

    def test_jsonListNotDicts(self, file_manager: FilesMngr, tmp_path: Path):
        """
        Test that load_examples_from_json accepts a list of non-dict items.
        If the JSON file contains a list of non-dict items, it should still return them
        """
        f: Path = tmp_path / "not_dicts.json"
        f.write_text(json.dumps(["a", "b", "c"]))
        result = file_manager.load_examples_from_json(f)
        assert result == [
            "a",
            "b",
            "c",
        ]  # should pass, since only type(list) is checked


# ---------------------------
# Tests for replaceFilename
# ---------------------------
class TestReplaceFilename:
    def test_basicReplacement(self, file_manager: FilesMngr):
        """
        Test that replaceFilename correctly replaces the filename in a path.
        Should return a new path with the updated filename
        """
        path: Path = Path("/tmp/somefile.txt")
        new = file_manager.replaceFilename(path, "new.txt")
        assert new == Path("/tmp/new.txt")

    def test_customPath(self, file_manager: FilesMngr):
        """
        Test that replaceFilename works with a custom path and new filename.
        Should return a new path with the updated filename
        """
        path: Path = Path("/path/to/old_file.txt")
        new_filename = "new_file.md"
        expected: Path = Path("/path/to/new_file.md")
        assert file_manager.replaceFilename(path, new_filename) == expected

    def test_noDirectoryComponent(self, file_manager: FilesMngr):
        """
        Test that replaceFilename works when the path has no directory component.
        Should return the new filename directly
        """
        path: Path = Path("file.txt")
        new = file_manager.replaceFilename(path, "new.txt")
        assert new == Path("new.txt")
