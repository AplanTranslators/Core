"""
Unit tests for Program.

Design rules:
- No mocking — all tests use real class instances.
- Atomic — one test, one behaviour.
- No multiple unrelated assertions per test.
- Full branch / line coverage of program.py.

Singleton isolation: Program is a singleton (SingletonMeta). Each test that
needs a clean Program instance must reset the singleton registry before
construction. A module-level fixture `reset_program` handles this by removing
Program from SingletonMeta._instances before and after each test, so every
test that uses it starts with a fresh object.

Filesystem isolation: Tests that exercise filesystem methods (create_result_directory,
write_to_file, readFileData, create_aplan_files) use Python's built-in
`tmp_path` pytest fixture so no permanent files are created and cleanup is
automatic.

Singleton counters: Counters is also a singleton. Tests that care about counter
state call counters.reinit() in setup to start from a known baseline.
"""

import os
import pytest
from pathlib import Path

from ..program.program import Program
from ..singleton.singleton import SingletonMeta
from ..classes.design_unit import DesignUnit, DesignUnitArray
from ..classes.typedef import Typedef, TypedefArray
from ..classes.declarations import DeclTypes
from ..classes.element_types import ElementsTypes
from ..utils.counters import Counters


# ===========================================================================
# Fixtures
# ===========================================================================

@pytest.fixture(autouse=False)
def reset_program():
    """
    Remove Program from the singleton registry before and after each test
    so every test that needs Program gets a fresh instance.
    """
    SingletonMeta._instances.pop(Program, None)
    yield
    SingletonMeta._instances.pop(Program, None)


@pytest.fixture()
def program(reset_program, tmp_path):
    """Fresh Program instance pointing at a real temp directory."""
    return Program(path_to_result=str(tmp_path))


@pytest.fixture()
def program_no_path(reset_program):
    """Fresh Program instance with no path_to_result supplied."""
    return Program()


@pytest.fixture()
def generated_program(program):
    """Program with result directory created and all aplan files generated."""
    program.create_result_dirrectory()
    program.create_aplan_files()
    return program


# ===========================================================================
# Helpers
# ===========================================================================

def make_design_unit(
    identifier="MOD",
    ident_uniq_name="mod",
    element_type=ElementsTypes.MODULE_ELEMENT,
) -> DesignUnit:
    return DesignUnit(
        identifier=identifier,
        ident_uniq_name=ident_uniq_name,
        element_type=element_type,
    )


def make_typedef(
    identifier="state_t",
    unique_identifier="mod_state_t",
    source_interval=(0, 5),
    file_path="/f.sv",
    data_type=DeclTypes.ENUM_TYPE,
) -> Typedef:
    return Typedef(
        identifier=identifier,
        unique_identifier=unique_identifier,
        source_interval=source_interval,
        file_path=file_path,
        data_type=data_type,
    )


# ===========================================================================
# 1. Program – __init__ and singleton behaviour
# ===========================================================================

class TestProgramInit:

    def test_is_singleton(self, reset_program):
        p1 = Program(path_to_result="/tmp/a")
        p2 = Program(path_to_result="/tmp/b")
        assert p1 is p2

    def test_path_to_result_is_stored(self, program):
        # strip the sep that create_result_directory may add; we test raw init
        assert program.path_to_result is not None

    def test_path_to_result_none_when_not_supplied(self, program_no_path):
        assert program_no_path.path_to_result is None

    def test_design_units_is_design_unit_array(self, program):
        assert isinstance(program.design_units, DesignUnitArray)

    def test_design_units_starts_empty(self, program):
        assert len(program.design_units) == 0

    def test_typedefs_property_returns_typedef_array(self, program):
        assert isinstance(program.typedefs, TypedefArray)

    def test_typedefs_starts_empty(self, program):
        assert len(program.typedefs) == 0

    def test_design_units_calls_property_returns_array(self, program):
        from ..classes.design_unit_call import DesignUnitCallArray
        assert isinstance(program.design_units_calls, DesignUnitCallArray)

    def test_logger_is_assigned(self, program):
        assert program.logger is not None

    def test_str_formater_is_singleton(self, program):
        from ..utils.string_formater import StringFormater
        assert isinstance(program.str_formater, StringFormater)

    def test_counters_is_singleton(self, program):
        assert isinstance(program.counters, Counters)


# ===========================================================================
# 2. Program – properties
# ===========================================================================

class TestProgramProperties:

    def test_typedefs_property_is_same_object_as_internal(self, program):
        assert program.typedefs is program._typedefs

    def test_design_units_calls_property_is_same_object_as_internal(self, program):
        assert program.design_units_calls is program.DesignUnit


# ===========================================================================
# 3. Program – readFileData()
# ===========================================================================

class TestProgramReadFileData:

    def test_returns_file_contents(self, program, tmp_path):
        f = tmp_path / "test.sv"
        f.write_text("module top; endmodule")
        result = program.readFileData(str(f))
        assert result == "module top; endmodule"

    def test_stores_file_path(self, program, tmp_path):
        f = tmp_path / "test.sv"
        f.write_text("")
        program.readFileData(str(f))
        assert program.file_path == str(f)

    def test_returns_string(self, program, tmp_path):
        f = tmp_path / "test.sv"
        f.write_text("content")
        result = program.readFileData(str(f))
        assert isinstance(result, str)

    def test_empty_file_returns_empty_string(self, program, tmp_path):
        f = tmp_path / "empty.sv"
        f.write_text("")
        assert program.readFileData(str(f)) == ""


# ===========================================================================
# 4. Program – create_result_directory()
# ===========================================================================

class TestProgramCreateResultDirectory:

    def test_creates_directory_when_not_exists(self, reset_program, tmp_path):
        new_dir = tmp_path / "output"
        p = Program(path_to_result=str(new_dir))
        p.create_result_dirrectory()
        assert new_dir.exists()

    def test_appends_sep_when_path_missing_trailing_sep(self, reset_program, tmp_path):
        path_str = str(tmp_path / "out")
        p = Program(path_to_result=path_str)
        p.create_result_dirrectory()
        assert p.path_to_result.endswith(os.sep)

    def test_does_not_double_append_sep(self, reset_program, tmp_path):
        path_str = str(tmp_path / "out") + os.sep
        p = Program(path_to_result=path_str)
        p.create_result_dirrectory()
        assert not p.path_to_result.endswith(os.sep + os.sep)

    def test_defaults_to_results_dir_when_path_is_none(self, reset_program, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        p = Program()
        p.create_result_dirrectory()
        assert p.path_to_result == "results" + os.sep

    def test_existing_directory_does_not_raise(self, program):
        program.create_result_dirrectory()
        # Call again — directory already exists
        program.create_result_dirrectory()


# ===========================================================================
# 5. Program – write_to_file()
# ===========================================================================

class TestProgramWriteToFile:

    def test_creates_file(self, program, tmp_path):
        out = tmp_path / "out.txt"
        program.write_to_file(str(out), "hello")
        assert out.exists()

    def test_writes_correct_content(self, program, tmp_path):
        out = tmp_path / "out.txt"
        program.write_to_file(str(out), "hello world")
        assert out.read_text() == "hello world"

    def test_overwrites_existing_file(self, program, tmp_path):
        out = tmp_path / "out.txt"
        out.write_text("old content")
        program.write_to_file(str(out), "new content")
        assert out.read_text() == "new content"

    def test_writes_empty_string(self, program, tmp_path):
        out = tmp_path / "out.txt"
        program.write_to_file(str(out), "")
        assert out.read_text() == ""

    def test_writes_multiline_content(self, program, tmp_path):
        out = tmp_path / "out.txt"
        program.write_to_file(str(out), "line1\nline2")
        assert out.read_text() == "line1\nline2"


# ===========================================================================
# 6. Program – create_aplan_files()
# ===========================================================================

class TestProgramCreateAplanFiles:

    def test_creates_beh_file(self, generated_program):
        assert os.path.exists(generated_program.path_to_result + "project.behp")

    def test_creates_env_file(self, generated_program):
        assert os.path.exists(generated_program.path_to_result + "project.env_descript")

    def test_creates_act_file(self, generated_program):
        assert os.path.exists(generated_program.path_to_result + "project.act")

    def test_creates_evt_file(self, generated_program):
        assert os.path.exists(generated_program.path_to_result + "project.evt_descript")

    def test_beh_file_is_string_content(self, generated_program):
        content = Path(generated_program.path_to_result + "project.behp").read_text()
        assert isinstance(content, str)

    def test_env_file_contains_environment_keyword(self, generated_program):
        content = Path(generated_program.path_to_result + "project.env_descript").read_text()
        assert "environment" in content

    def test_evt_file_contains_events_keyword(self, generated_program):
        content = Path(generated_program.path_to_result + "project.evt_descript").read_text()
        assert "events" in content

    def test_counters_are_reinitialized_after_call(self, program):
        program.create_result_dirrectory()
        counters = program.counters
        counters.incriese(counters.types.ASSIGNMENT_COUNTER)
        program.create_aplan_files()
        assert counters.get(counters.types.ASSIGNMENT_COUNTER) == 1

    def test_create_aplan_files_with_design_unit(self, program):
        """Smoke test: adding a real DesignUnit does not crash file generation."""
        program.create_result_dirrectory()
        du = make_design_unit()
        program.design_units.addElement(du)
        program.create_aplan_files()
        assert os.path.exists(program.path_to_result + "project.behp")

    def test_create_aplan_files_with_typedef(self, program):
        """Smoke test: adding a typedef does not crash env file generation."""
        program.create_result_dirrectory()
        program.typedefs.addElement(make_typedef())
        program.create_aplan_files()
        assert os.path.exists(program.path_to_result + "project.env_descript")

    def test_env_file_contains_nil_when_no_declarations(self, program):
        """With no declarations, agent types section should contain Nil."""
        program.create_result_dirrectory()
        du = make_design_unit()
        program.design_units.addElement(du)
        program.create_aplan_files()
        content = Path(program.path_to_result + "project.env_descript").read_text()
        assert "Nil" in content

    def test_object_element_excluded_from_beh(self, program):
        """
        DesignUnits with OBJECT_ELEMENT are excluded from beh file generation.
        This tests the getElementsIE(exclude=OBJECT_ELEMENT) branch in beh.py.
        """
        program.create_result_dirrectory()
        du_obj = make_design_unit(
            identifier="OBJ",
            ident_uniq_name="obj_inst",
            element_type=ElementsTypes.OBJECT_ELEMENT,
        )
        program.design_units.addElement(du_obj)
        program.create_aplan_files()
        content = Path(program.path_to_result + "project.behp").read_text()
        assert "OBJ" not in content

    def test_class_element_excluded_from_agents_in_env(self, program):
        """
        CLASS_ELEMENT design units are excluded from the agents section in env.
        This tests the getElementsIE(exclude=CLASS_ELEMENT) branch in env.py.
        """
        program.create_result_dirrectory()
        du_cls = make_design_unit(
            identifier="CLS",
            ident_uniq_name="cls_inst",
            element_type=ElementsTypes.CLASS_ELEMENT,
        )
        program.design_units.addElement(du_cls)
        program.create_aplan_files()
        content = Path(program.path_to_result + "project.env_descript").read_text()
        agents_section = content.split("agents")[1] if "agents" in content else ""
        assert "cls_inst" not in agents_section


# ===========================================================================
# 7. Known bugs
# ===========================================================================

BUG_SINGLETON_INIT_IGNORES_NEW_PATH = (
    "BUG: Program is a singleton (SingletonMeta). Once constructed, subsequent "
    "calls to Program(path_to_result=...) silently return the existing instance "
    "without updating path_to_result. Callers expecting a new instance with a "
    "different path will get stale configuration."
)


class TestProgramKnownBugs:

    @pytest.mark.xfail(strict=True, reason=BUG_SINGLETON_INIT_IGNORES_NEW_PATH)
    def test_second_construction_with_different_path_updates_path(self, reset_program, tmp_path):
        path_a = str(tmp_path / "a")
        path_b = str(tmp_path / "b")
        Program(path_to_result=path_a)
        p2 = Program(path_to_result=path_b)
        assert p2.path_to_result == path_b