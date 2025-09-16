import pytest
from ..classes.action_precondition import ActionPrecondition, ActionPreconditionArray


# -----------------------
# Tests for ActionPrecondition
# -----------------------

class TestActionPrecondition:
    """Unit tests for ActionPrecondition class."""

    # --- Initialization & Defaults ---
    def test_init_sets_precondition(self):
        """ Tests that precondition should be set from constructor """
        obj = ActionPrecondition("a <= b")
        assert obj.precondition == "a <= b"

    def test_inherits_identifier_from_basic(self):
        """ Tests that identifier should default to "" from Basic"""
        obj = ActionPrecondition("a > 0")
        assert obj.identifier == ""

    def test_inherits_source_interval_from_basic(self):
        """ Tests that source_interval should default to (0,0) from Basic"""
        obj = ActionPrecondition("a > 0")
        assert obj.source_interval == (0, 0)

    
    # --- String & Representation ---
    def test_str_returns_precondition(self):
        """Tests that __str__ returns the precondition string."""
        obj = ActionPrecondition("b >= a")
        assert str(obj) == "b >= a"

    def test_repr_format(self):
        """Tests that repr() should show the class name, identifier, and precondition"""
        obj = ActionPrecondition("b == 0")
        assert repr(obj) == "ActionPrecondition('', 'b == 0')\n"


# -----------------------
# Tests for ActionPreconditionArray
# -----------------------

@pytest.fixture
def precondition_array():
    """
    Fixture: creates a pre-filled ActionPreconditionArray with 2 conditions.
    Used in multiple tests for consistency.
    """
    arr = ActionPreconditionArray()
    arr.addElement(ActionPrecondition("a != 0"))
    arr.addElement(ActionPrecondition("b == 0"))
    return arr


class TestActionPreconditionArray:
    """Unit tests for ActionPreconditionArray class."""

    # --- Initialization ---
    def test_init_sets_type(self):
        """Tests that ActionPreconditionArray initializes with correct element_type."""
        arr = ActionPreconditionArray()
        assert arr.element_type is ActionPrecondition

    # --- String & Representation ---
    def test_str_empty(self):
        # Empty array → str() should return an empty string
        arr = ActionPreconditionArray()
        assert str(arr) == ""

    def test_str_single_element(self):
        """Tests that __str__ returns the precondition of the single element."""
        arr = ActionPreconditionArray()
        arr.addElement(ActionPrecondition("c <= b"))
        assert str(arr) == "c <= b"

    def test_str_multiple_elements(self):
        """Tests that __str__ joins multiple preconditions with semicolons."""
        arr = ActionPreconditionArray()
        arr.addElement(ActionPrecondition("x > 0"))
        arr.addElement(ActionPrecondition("y < 10"))
        assert str(arr) == "x > 0;y < 10"

    def test_repr_full(self, precondition_array):
        """Tests that repr() shows all elements in the array."""
        expected = f"ActionPreconditionArray(\n{precondition_array.elements!r}\t)"
        assert repr(precondition_array) == expected

    
    # --- Collection Behavior (iteration, indexing, copy, getElements) ---
    def test_iteration(self, precondition_array):
        """Tests that iterating over the array yields ActionPrecondition instances."""
        elements = list(precondition_array)
        assert all(isinstance(e, ActionPrecondition) for e in elements)
        assert str(elements[0]) == "a != 0"
        assert str(elements[1]) == "b == 0"

    def test_indexing(self, precondition_array):
        """Tests that indexing returns the correct ActionPrecondition."""
        first = precondition_array[0]
        assert isinstance(first, ActionPrecondition)
        assert str(first) == "a != 0"

    def test_copy_independence(self, precondition_array):
        copied = precondition_array.copy()
        copied.addElement(ActionPrecondition("c < 10"))
        assert len(copied) == 3
        assert len(precondition_array) == 2  # unchanged

    def test_get_elements_length(self, precondition_array):
        elements = precondition_array.getElements()
        assert len(elements) == 2

    def test_get_elements_first(self, precondition_array):
        """Tests that getElements returns the correct elements."""
        elements = precondition_array.getElements()
        assert str(elements[0]) == "a != 0"

    def test_invalid_index_raises(self):
        """Testing that accessing an index that does not exist should raise IndexError."""
        arr = ActionPreconditionArray()
        with pytest.raises(IndexError):
            _ = arr[0]

    def test_add_invalid_element_logs_warning(self, caplog):
        """Adding an invalid type should log a warning."""
        arr = ActionPreconditionArray()
        with caplog.at_level("WARNING"):
            arr.addElement("not_a_precondition")

        # The element is added, but a warning is logged
        assert "Object should be of type ActionPrecondition" in caplog.text
        assert len(arr) == 1  # still added
