import pytest
from ..classes.case_stmt import CaseStmt
from ..classes.element_types import ElementsTypes


class TestCaseStmtInitialization:
    """Tests for CaseStmt.__init__ behavior and inherited attributes."""

    def test_initializes_with_expected_defaults(self):
        """CaseStmt: initializes with correct defaults and element type."""
        c = CaseStmt("case1", (10, 20))
        assert c.identifier == "case1"
        assert c.source_interval == (10, 20)
        assert c.element_type == ElementsTypes.CASE_STATEMENT_ELEMENT
        assert c.expression is None
        assert c.init_case_count == 0
        assert c.case_count == 0

    def test_inherits_from_structure(self):
        """Ensure CaseStmt inherits core methods from Structure."""
        c = CaseStmt("inheritTest", (0, 1))
        assert hasattr(c, "getName")
        assert callable(c.getName)
        assert hasattr(c, "logger")

    def test_allows_non_string_identifier(self):
        """CaseStmt: identifier can technically be non-string (edge case)."""
        c = CaseStmt(123, (0, 1))
        assert isinstance(c.identifier, int)
        assert "123" in repr(c)


class TestCaseStmtSetCaseCount:
    """Tests for setCaseCount() method."""

    def test_set_case_count_updates_both_fields(self):
        """setCaseCount: sets both init_case_count and case_count."""
        c = CaseStmt("case_block", (0, 1))
        c.setCaseCount(7)
        assert c.init_case_count == 7
        assert c.case_count == 7

    @pytest.mark.parametrize("count", [0, 1, 10])
    def test_set_case_count_multiple_values(self, count):
        """setCaseCount: works correctly for multiple integer values."""
        c = CaseStmt("case_param", (1, 2))
        c.setCaseCount(count)
        assert c.init_case_count == count
        assert c.case_count == count

    def test_set_case_count_called_twice_overwrites_values(self):
        """setCaseCount: calling twice should overwrite both fields."""
        c = CaseStmt("overwrite_case", (1, 2))
        c.setCaseCount(3)
        c.setCaseCount(8)
        assert c.init_case_count == 8
        assert c.case_count == 8

    def test_set_case_count_negative_value(self):
        """setCaseCount: accepts negative values (though semantically invalid)."""
        c = CaseStmt("neg_case", (1, 2))
        c.setCaseCount(-5)
        assert c.init_case_count == -5
        assert c.case_count == -5


class TestCaseStmtExpression:
    """Tests for handling the expression attribute."""

    def test_expression_can_be_set_and_read(self):
        """CaseStmt: allows assigning expression manually."""
        c = CaseStmt("expr_case", (1, 2))
        mock_expr = "a + b"
        c.expression = mock_expr
        assert c.expression == "a + b"

    def test_expression_none_repr_safe(self):
        """CaseStmt: expression=None handled gracefully in __repr__."""
        c = CaseStmt("expr_none", (1, 2))
        c.expression = None
        assert "expression=None" in repr(c)

    def test_expression_special_characters(self):
        """CaseStmt: expression with special characters handled safely in __repr__."""
        expr = "data[0] == 0xFF && enable /* comment */"
        c = CaseStmt("expr_special", (3, 9))
        c.expression = expr
        out = repr(c)
        assert "0xFF" in out
        assert "enable" in out


class TestCaseStmtRepr:
    """Tests for __repr__ output formatting and content."""

    def test_repr_includes_identifier_and_case_counts(self):
        """__repr__: includes identifier, counts, and sequence info."""
        c = CaseStmt("case_repr", (2, 3))
        c.expression = "x == y"
        c.setCaseCount(5)
        result = repr(c)
        assert "CaseStmt" in result
        assert "case_repr" in result
        assert "x == y" in result
        assert "init_case_count=5" in result
        assert "case_count=5" in result
        assert "sequence=" in result

    def test_repr_handles_missing_expression_and_sequence(self):
        """__repr__: handles missing expression and sequence gracefully."""
        c = CaseStmt("no_expr", (0, 5))
        if hasattr(c, "sequence"):
            delattr(c, "sequence")
        result = repr(c)
        assert "expression=None" in result
        assert "sequence='N/A'" in result

    def test_repr_handles_long_expression(self):
        """__repr__: properly truncates or includes very long expressions."""
        long_expr = " + ".join([f"sig{i}" for i in range(50)])
        c = CaseStmt("long_case", (10, 20))
        c.expression = long_expr
        out = repr(c)
        assert "sig0" in out
        assert "sig49" in out
        assert "CaseStmt" in out

    def test_repr_handles_unusual_identifier(self):
        """__repr__: identifier with unusual characters is handled safely."""
        c = CaseStmt("case@#$_Name", (1, 2))
        c.expression = "value == 1"
        result = repr(c)
        assert "case@#$_Name" in result
        assert "CaseStmt" in result


class TestCaseStmtIntegration:
    """Integration-like tests combining multiple behaviors."""

    def test_sequence_field_reflected_in_repr(self):
        """CaseStmt: sequence value from Structure appears in __repr__."""
        c = CaseStmt("seq_case", (1, 2))
        c.sequence = 42
        output = repr(c)
        assert "sequence=42" in output

    def test_changing_case_count_does_not_affect_init_case_count(self):
        """CaseStmt: manually changing case_count doesn't alter init_case_count."""
        c = CaseStmt("case_modify", (0, 1))
        c.setCaseCount(3)
        c.case_count = 1
        assert c.init_case_count == 3
        assert c.case_count == 1

    def test_repr_after_multiple_mutations(self):
        """CaseStmt: __repr__ remains valid after several mutations."""
        c = CaseStmt("mutated_case", (5, 10))
        c.expression = "sig_a && sig_b"
        c.setCaseCount(10)
        c.case_count = 7
        c.sequence = 99
        out = repr(c)
        assert "sig_a" in out
        assert "case_count=7" in out
        assert "sequence=99" in out

    def test_repr_still_safe_after_attribute_deletion(self):
        """CaseStmt: deleting several attributes does not cause __repr__ failure."""
        c = CaseStmt("del_case", (0, 1))
        del c.expression
        del c.init_case_count
        del c.case_count
        # __repr__ should not raise exception even if some fields missing
        out = repr(c)
        assert "CaseStmt" in out
        assert "identifier='del_case'" in out
