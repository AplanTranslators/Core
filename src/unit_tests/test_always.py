# src/unit_tests/test_always.py
import pytest
from ..classes.always import Always

# -------------------------------------------------------------
# Test class: TestAlwaysInitialization
# Purpose: Verify correct initialization behavior of Always class.
# -------------------------------------------------------------
class TestAlwaysInitialization:
    def test_init_with_sensitivity(self):
        """Always: should correctly store identifier, sensitivity, and source interval."""
        a = Always("clk_block", "@(posedge clk)", (1, 5))
        assert a.identifier == "clk_block"
        assert a.sensetive == "@(posedge clk)"
        assert a.source_interval == (1, 5)

    def test_init_without_sensitivity(self):
        """Always: sensitivity can be None."""
        a = Always("idle_loop", None, (10, 20))
        assert a.sensetive is None
        assert a.identifier == "idle_loop"
        assert a.source_interval == (10, 20)


# -------------------------------------------------------------
# Test class: TestAlwaysGetSensetiveForB0
# Purpose: Ensure getSensetiveForB0 returns correct formatted string
# -------------------------------------------------------------
class TestAlwaysGetSensetiveForB0:
    def test_with_sensitivity(self, monkeypatch):
        """getSensetiveForB0: should include both name and sensitivity list."""
        a = Always("process_block", "@(posedge clk or negedge rst)", (0, 1))

        # Monkeypatch getName from Structure to return predictable name
        monkeypatch.setattr(a, "getName", lambda: "process_block")

        expected = "Sensetive(process_block, @(posedge clk or negedge rst))"
        assert a.getSensetiveForB0() == expected

    def test_without_sensitivity(self, monkeypatch):
        """getSensetiveForB0: if no sensitivity, returns just the block name."""
        a = Always("background_loop", None, (0, 1))
        monkeypatch.setattr(a, "getName", lambda: "background_loop")

        expected = "background_loop"
        assert a.getSensetiveForB0() == expected


# -------------------------------------------------------------
# Test class: TestAlwaysRepr
# Purpose: Verify developer-friendly string representation (__repr__)
# -------------------------------------------------------------
class TestAlwaysRepr:
    def test_repr_with_sequence_and_sensitivity(self):
        """__repr__: includes identifier, sensitivity, and sequence when available."""
        a = Always("seq_logic", "@(posedge clk)", (5, 10))
        a.sequence = 42  # simulate inherited sequence from Structure
        result = repr(a)
        assert "Always" in result
        assert "seq_logic" in result
        assert "@(posedge clk)" in result
        assert "42" in result

    def test_repr_without_sequence(self):
        """__repr__: if sequence defined (default=0), displays numeric value."""
        a = Always("no_seq", "@(negedge rst)", (1, 2))
        result = repr(a)
        assert "Always" in result
        assert "sequence=0" in result  # Adjusted expectation


    def test_repr_with_sensitivity_but_no_sequence(self):
        """__repr__: covers the case where sensitivity is present but sequence is missing ('N/A')."""
        
        a = Always("full_repr_no_seq", "@(trigger)", (1, 2))
        
        # Ensure the 'sequence' attribute is NOT present on the instance.
        if hasattr(a, 'sequence'):
            del a.sequence
            
        result = repr(a)
        
        assert "Always" in result
        assert "full_repr_no_seq" in result
        assert "@(trigger)" in result       # Check sensitivity is present
        assert "sequence='N/A'" in result   # Check sequence fallback


# -------------------------------------------------------------
# Test class: TestAlwaysEdgeCases
# Purpose: Cover boundary/edge scenarios to reach 100% coverage.
# -------------------------------------------------------------
class TestAlwaysEdgeCases:
    def test_empty_identifier(self, monkeypatch):
        """Edge case: empty identifier still handled gracefully."""
        a = Always("", None, (0, 0))
        monkeypatch.setattr(a, "getName", lambda: "")
        assert a.getSensetiveForB0() == ""
        assert "Always" in repr(a)

    def test_long_sensitivity_string(self, monkeypatch):
        """Edge case: long sensitivity strings are fully preserved."""
        long_sens = "@(" + " or ".join([f"sig{i}" for i in range(50)]) + ")"
        a = Always("heavy_block", long_sens, (0, 10))
        monkeypatch.setattr(a, "getName", lambda: "heavy_block")
        res = a.getSensetiveForB0()
        assert "sig49" in res
        assert res.startswith("Sensetive(")
