import pytest
from ..classes.element_types import ElementsTypes
from ..classes.basic import BasicArray
from ..classes.structure import Structure
from ..classes.loop_stmt import LoopStmt, ForeverStmt, WhileStmt


# ===============================================================
#  TESTS FOR LoopStmt
# ===============================================================
class TestLoopStmtInitialization:
    """
    Tests for verifying correct initialization of LoopStmt instances.
    """

    def test_loopstmt_basic_initialization(self):
        """Ensure LoopStmt correctly sets identifier, interval, and flags."""
        stmt = LoopStmt("loopA", (5, 10))

        assert stmt.identifier == "loopA"
        assert stmt.source_interval == (5, 10)
        assert stmt.element_type == ElementsTypes.LOOP_ELEMENT
        assert stmt.is_loop is True

    def test_loopstmt_is_instance_of_structure(self):
        """Ensure LoopStmt inherits from Structure."""
        stmt = LoopStmt("loopB", (1, 3))
        assert isinstance(stmt, Structure)

    def test_loopstmt_behavior_attribute(self):
        """Confirm inherited 'behavior' attribute exists and is a list."""
        stmt = LoopStmt("loopC", (10, 15))
        assert hasattr(stmt, "behavior")
        assert isinstance(stmt.behavior, list)

    def test_loopstmt_elements_and_parametrs_attributes(self):
        """Confirm inherited 'elements' and 'parametrs' attributes exist with correct types."""
        stmt = LoopStmt("loopC", (10, 15))
        assert hasattr(stmt, "elements")
        assert isinstance(stmt.elements, BasicArray)
        
        assert hasattr(stmt, "parametrs")


class TestLoopStmtRepr:
    """
    Tests for __repr__() correctness and coverage.
    """

    def test_repr_contains_identifier_and_sequence(self):
        """Check repr string contains all expected key values."""
        stmt = LoopStmt("loopRepr", (0, 1))
        repr_str = repr(stmt)

        assert "LoopStmt" in repr_str
        assert "loopRepr" in repr_str
        assert "sequence=0" in repr_str

    def test_repr_with_custom_number(self):
        """Simulate name_space_level attribute and verify repr output."""
        stmt = LoopStmt("customLoop", (2, 3))
        stmt.number = 99  # Simulate inherited name_space_level storage
        repr_str = repr(stmt)

        assert "name_space_level=99" in repr_str


# ===============================================================
#  TESTS FOR ForeverStmt
# ===============================================================
class TestForeverStmtInitialization:
    """
    Tests for verifying ForeverStmt initialization and inheritance.
    """

    def test_foreverstmt_basic_initialization(self):
        """Ensure ForeverStmt correctly sets identifier, interval, and flags."""
        stmt = ForeverStmt("foreverA", (0, 5))

        assert stmt.identifier == "foreverA"
        assert stmt.source_interval == (0, 5)
        assert stmt.element_type == ElementsTypes.FOREVER_ELEMENT
        assert stmt.is_forever is True

    def test_foreverstmt_is_instance_of_structure(self):
        """Ensure ForeverStmt inherits from Structure."""
        stmt = ForeverStmt("foreverB", (1, 2))
        assert isinstance(stmt, Structure)

    def test_foreverstmt_inheritance_integrity(self):
        """Confirm inherited Structure attributes remain intact."""
        stmt = ForeverStmt("foreverC", (3, 9))
        assert hasattr(stmt, "elements")
        assert isinstance(stmt.elements, BasicArray)
        assert hasattr(stmt, "parametrs")


class TestForeverStmtRepr:
    """
    Tests for verifying __repr__() of ForeverStmt.
    """

    def test_repr_contains_identifier_and_sequence(self):
        """Check repr string shows essential details."""
        stmt = ForeverStmt("foreverRepr", (5, 10))
        repr_str = repr(stmt)

        assert "ForeverStmt" in repr_str
        assert "foreverRepr" in repr_str
        assert "sequence=0" in repr_str

    def test_repr_with_custom_number(self):
        """Ensure custom number (namespace level) appears correctly."""
        stmt = ForeverStmt("foreverCustom", (4, 8))
        stmt.number = 42
        repr_str = repr(stmt)

        assert "name_space_level=42" in repr_str


# ===============================================================
#  TESTS FOR WhileStmt
# ===============================================================
class TestWhileStmtInitialization:
    """
    Tests for verifying correct initialization of WhileStmt instances.
    """

    def test_whilestmt_basic_initialization(self):
        """Ensure WhileStmt correctly sets identifier, interval, and flags."""
        stmt = WhileStmt("whileA", (0, 4))

        assert stmt.identifier == "whileA"
        assert stmt.source_interval == (0, 4)
        assert stmt.element_type == ElementsTypes.WHILE_ELEMENT
        assert stmt.is_while is True

    def test_whilestmt_is_instance_of_structure(self):
        """Ensure WhileStmt inherits from Structure."""
        stmt = WhileStmt("whileB", (1, 2))
        assert isinstance(stmt, Structure)

    def test_whilestmt_inheritance_integrity(self):
        """Confirm inherited Structure properties exist."""
        stmt = WhileStmt("whileC", (6, 12))
        assert hasattr(stmt, "elements")
        assert hasattr(stmt, "parametrs")
        assert isinstance(stmt.behavior, list)


class TestWhileStmtRepr:
    """
    Tests for verifying __repr__() of WhileStmt.
    """

    def test_repr_contains_identifier_and_sequence(self):
        """Check repr string contains essential details."""
        stmt = WhileStmt("whileRepr", (2, 6))
        repr_str = repr(stmt)

        assert "WhileStmt" in repr_str
        assert "whileRepr" in repr_str
        assert "sequence=0" in repr_str

    def test_repr_with_custom_number(self):
        """Ensure repr reflects custom number when assigned."""
        stmt = WhileStmt("whileCustom", (7, 14))
        stmt.number = 77
        repr_str = repr(stmt)

        assert "name_space_level=77" in repr_str


# ===============================================================
#  EXTRA ROBUSTNESS TESTS (shared behavior)
# ===============================================================
class TestLoopHierarchyBehavior:
    """
    Shared tests ensuring consistency across LoopStmt variants.
    """

    @pytest.mark.parametrize("cls,flag_attr", [
        (LoopStmt, "is_loop"),
        (ForeverStmt, "is_forever"),
        (WhileStmt, "is_while"),
    ])
    def test_each_loop_type_has_correct_flag(self, cls, flag_attr):
        """Ensure each subclass defines its own loop indicator flag."""
        stmt = cls("flagCheck", (0, 1))
        assert getattr(stmt, flag_attr) is True

    @pytest.mark.parametrize("cls", [LoopStmt, ForeverStmt, WhileStmt])
    def test_repr_handles_missing_sequence_gracefully(self, cls):
        """Ensure repr does not crash if sequence attribute is missing."""
        stmt = cls("noSeq", (0, 2))
        delattr(stmt, "sequence")  # simulate attribute absence
        repr_str = repr(stmt)
        # Should still render cleanly with 'N/A'
        assert "sequence='N/A'" in repr_str
