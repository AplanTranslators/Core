import pytest
from ..classes.element_types import ElementsTypes
from ..classes.if_stmt import IfStmt
from ..classes.structure import Structure



class TestIfStmtInitialization:
    """
    Tests for verifying correct initialization behavior of IfStmt objects.
    """

    def test_initialization_basic(self):
        """Ensure that constructor sets identifier, element_type, and default counters correctly."""
        stmt = IfStmt("if_block", (10, 20))

        # Basic inherited fields
        assert stmt.identifier == "if_block"
        assert stmt.source_interval == (10, 20)
        assert stmt.element_type == ElementsTypes.IF_STATEMENT_ELEMENT

        # Default counter values
        assert stmt.if_count == 0
        assert stmt.else_count == 0
        assert stmt.last_step == 0
        assert stmt.step == 1

    def test_initialization_type(self):
        """Ensure IfStmt is an instance of Structure and inherits Structure properties."""
        stmt = IfStmt("cond_check", (0, 5))
        assert isinstance(stmt, Structure)


class TestSetCondCount:
    """
    Tests for setCondCount(), which updates internal branch counters.
    """

    def test_set_cond_count_basic(self):
        """Test standard case where if_count != else_count."""
        stmt = IfStmt("if_case", (1, 2))
        stmt.setCondCount(3, 1)

        # Should set values directly
        assert stmt.if_count == 3
        assert stmt.else_count == 1
        # Since if_count != else_count, last_step remains default (0)
        assert stmt.last_step == 0
        # Resets step to 1
        assert stmt.step == 1

    def test_set_cond_count_equal_counts(self):
        """If if_count == else_count, last_step should be incremented by 1."""
        stmt = IfStmt("if_else_pair", (2, 4))
        stmt.setCondCount(2, 2)

        # Expect computed value
        assert stmt.last_step == 3  # 2 + 1
        assert stmt.step == 1

    def test_set_cond_count_zero_case(self):
        """Handles zero if/else counts without errors."""
        stmt = IfStmt("empty_if", (0, 1))
        stmt.setCondCount(0, 0)

        assert stmt.if_count == 0
        assert stmt.else_count == 0
        assert stmt.last_step == 1
        assert stmt.step == 1

    def test_set_cond_count_mutation(self):
        """Ensure setCondCount mutates internal state and not returns a new object."""
        stmt = IfStmt("mut_case", (5, 9))
        old_id = id(stmt)
        stmt.setCondCount(1, 1)
        assert id(stmt) == old_id  # same object, no copy made

    def test_set_cond_count_resets_step(self):
        """Ensure setCondCount resets the step attribute to 1, regardless of its previous value."""
        stmt = IfStmt("reset_test", (1, 3))
        # Manually set step to simulate traversal deep into the block
        stmt.step = 5 
        # Call setCondCount, which should reset self.step = 1 at the end
        stmt.setCondCount(2, 2) 
        
        # Verify the reset happened
        assert stmt.step == 1 
        # Optionally, verify other attributes were set correctly
        assert stmt.if_count == 2
        assert stmt.last_step == 3

    def test_large_counts(self):
        """Ensure large branch counts are handled without overflow or logic errors."""
        stmt = IfStmt("large_case", (5, 10))
        stmt.setCondCount(1000, 999)
        assert stmt.if_count == 1000
        assert stmt.else_count == 999
        assert stmt.last_step == 0  # not equal, so no increment

    def test_equal_large_counts(self):
        """Large but equal counts should still increment correctly."""
        stmt = IfStmt("large_equal", (0, 5))
        stmt.setCondCount(100, 100)
        assert stmt.last_step == 101


class TestIfStmtRepr:
    """
    Tests for verifying the correctness and readability of __repr__().
    """

    def test_repr_includes_identifier(self):
        """Ensure the repr string includes identifier and key fields."""
        stmt = IfStmt("id_block", (0, 10))
        stmt.setCondCount(2, 1)
        repr_str = repr(stmt)

        assert "IfStmt" in repr_str
        assert "id_block" in repr_str
        assert "if_count=2" in repr_str
        assert "else_count=1" in repr_str
        assert "current_step=1" in repr_str

    def test_repr_includes_last_step_when_equal(self):
        """If if_count == else_count, repr should show updated last_step."""
        stmt = IfStmt("branch_match", (10, 20))
        stmt.setCondCount(2, 2)
        repr_str = repr(stmt)
        assert "last_step=3" in repr_str

    def test_repr_handles_missing_sequence(self):
        """Ensure repr gracefully handles missing inherited sequence attribute."""
        stmt = IfStmt("missing_seq", (1, 2))
        repr_str = repr(stmt)
        assert "sequence=0" in repr_str

    def test_repr_handles_empty_identifier(self):
        """Ensure repr() handles empty or unusual identifiers gracefully."""
        stmt = IfStmt("", (0, 0))
        stmt.setCondCount(0, 0)
        repr_str = repr(stmt)
        assert "IfStmt" in repr_str
        assert "identifier=''" in repr_str
