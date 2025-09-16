import pytest
from ..classes.actions import ActionParts, Action, ActionArray
from ..classes.parametrs import Parametr, ParametrArray
from ..classes.node import NodeArray
from ..classes.element_types import ElementsTypes


# -------------------
# Fixtures
# -------------------

@pytest.fixture
def sample_action_parts():
    """
    Provides an ActionParts instance with a pre-defined body.
    Used to test __str__, __repr__, and copy behavior.
    """
    parts = ActionParts()
    parts.body = ["part1", "part2"]
    return parts

@pytest.fixture
def sample_parametr_array():
    """
    Provides a ParametrArray with two parameters.
    Used to test actions with existing parameters.
    """
    arr = ParametrArray()
    arr.addElement(Parametr("x", "int", (0, 1)))
    arr.addElement(Parametr("y", "int", (2, 3)))
    return arr

@pytest.fixture
def sample_action(sample_parametr_array):
    """
    Provides a fully initialized Action object:
    - Has description_start, description_action_name, description_end.
    - Includes a ParametrArray for exist_parametrs.
    """
    action = Action("test_action", (1, 10), sample_parametr_array, ElementsTypes.ACTION_ELEMENT)
    action.description_start = ["init"]
    action.description_action_name = "DoSomething"
    action.description_end = ["done"]
    return action

@pytest.fixture
def action_array(sample_action):
    """
    Provides an ActionArray containing one sample action.
    Used to test array methods like copy, filtering, and uniqueness checks.
    """
    arr = ActionArray()
    arr.addElement(sample_action)
    return arr


# -------------------
# Tests for ActionParts
# -------------------

class TestActionParts:

    def test_init_and_str_repr(self):
        """Test default initialization, __str__, and __repr__ of ActionParts."""
        # Default init should start with empty body
        ap = ActionParts()
        assert ap.body == []

    def test_str_representation(self):
        # __str__ should join with "; "
        ap = ActionParts()
        ap.body.extend(["step1", "step2"])
        assert str(ap) == "step1; step2"

    def test_repr_representation(self):
        ap = ActionParts()
        ap.body.extend(["step1", "step2"])
        # __repr__ should include class name and list
        assert "ActionParts" in repr(ap)
        assert "step1" in repr(ap)
        assert repr(ap) == "ActionParts(body=['step1', 'step2'])"

    def test_copy_creates_independent_copy(self, sample_action_parts):
        """Test that copy() creates an independent ActionParts instance."""
        copy = sample_action_parts.copy()
        assert copy is not sample_action_parts
        assert copy.body == sample_action_parts.body

        # Modifying copy should not affect original
        copy.body.append("new")
        assert copy.body != sample_action_parts.body

    def test_str_and_repr(self, sample_action_parts):
        """Ensure __str__ and __repr__ return expected formats."""
        assert str(sample_action_parts) == "part1; part2"
        assert "ActionParts" in repr(sample_action_parts)


# -------------------
# Tests for Action
# -------------------

class TestAction:

    def test_init_with_defaults(self):
        """Test that Action initializes correctly with default values."""
        action = Action("test_action", (0, 0))
        assert action.identifier == "test_action"
        assert action.exist_parametrs is not None
        assert len(action.exist_parametrs.getElements()) == 0
        assert len(action.parametrs.getElements()) == 0

    def test_copy_creates_deep_copy(self, sample_action):
        """Test that copy() creates a deep copy of all mutable attributes."""
        copy = sample_action.copy()
        assert copy is not sample_action
        assert copy.identifier == sample_action.identifier
        
        # Check that mutable objects are independent copies
        assert copy.exist_parametrs is not sample_action.exist_parametrs
        assert copy.precondition is not sample_action.precondition
        assert copy.postcondition is not sample_action.postcondition
        assert copy.description_start is not sample_action.description_start
        assert copy.description_end is not sample_action.description_end


    def test_get_name_variants(self, sample_action):
        """Test Action.getName() with and without to_upper flag."""
        name_default = sample_action.getName()
        assert "test_action" in name_default

        name_upper = sample_action.getName(to_upper=True)
        assert "TEST_ACTION" in name_upper

    def test_get_name_with_number_and_params(self, sample_action):
        """Test getName() includes number and parameters correctly."""
        sample_action.number = 5
        sample_action.parametrs.addElement(Parametr("p1", "type1", (0, 1)))
        name = sample_action.getName()
        assert "test_action_5" in name
        assert "p1" in name

    def test_get_body_with_exist_params(self, sample_action):
        """Test Action.getBody() returns a string containing description and action name."""
        body = sample_action.getBody()
        # Should contain the :action keyword
        assert ":action" in body
        # Should include the description action name
        assert "DoSomething" in body
        # Should include start and end descriptions
        assert "init" in body
        assert "done" in body
        # Should include precondition/postcondition placeholders
        assert str(sample_action.precondition) in body
        assert str(sample_action.postcondition) in body

    def test_equality_with_identical_body(self, sample_action):
        """Two actions with the same body content should be equal."""
        identical_action = sample_action.copy()
        assert sample_action == identical_action

    def test_inequality_with_different_body(self, sample_action):
        """Two actions with different body content should not be equal."""
        different_action = sample_action.copy()
        different_action.description_action_name = "AnotherThing"
        assert sample_action != different_action

    def test_inequality_when_different_body(self, sample_action):
        diff_action = sample_action.copy()
        diff_action.description_action_name = "OtherThing"
        assert sample_action != diff_action

    def test_str_and_repr(self, sample_action):
        """Test __str__ and __repr__ of Action for readability and debugging."""
        s = str(sample_action)
        assert sample_action.identifier in s  # String representation includes identifier

        r = repr(sample_action)
        assert "Action" in r


# -------------------
# Tests for ActionArray
# -------------------

class TestActionArray:

    def test_copy_creates_deep_copy(self, action_array):
        """Test that ActionArray.copy() duplicates all contained Actions independently."""
        copy = action_array.copy()
        assert copy is not action_array
        assert copy.getElements()[0] is not action_array.getElements()[0]

    def test_get_elements_ie_with_filters(self, action_array, sample_action):
        """Test filtering ActionArray elements by include/exclude criteria."""
        # Include by element_type
        included = action_array.getElementsIE(include=sample_action.element_type)
        assert included.getElements()[0] == sample_action

        # Exclude by element_type
        excluded = action_array.getElementsIE(exclude=sample_action.element_type)
        assert len(excluded.getElements()) == 0

        # Include by identifier
        included_by_id = action_array.getElementsIE(include_identifier="test_action")
        assert included_by_id.getElements()[0] == sample_action

        # Exclude by identifier
        excluded_by_id = action_array.getElementsIE(exclude_identifier="test_action")
        assert len(excluded_by_id.getElements()) == 0

    def test_is_uniq_action_and_by_source_interval(self, action_array, sample_action):
        """Test uniqueness checks using ActionArray methods."""
        # Check uniqueness by content
        found, identifier, interval = action_array.isUniqAction(sample_action)
        assert found == sample_action
        assert identifier == "test_action"
        assert interval == (1, 10)

        # Check uniqueness by source_interval
        found_by_interval = action_array.isUniqActionBySourceInterval((1, 10))
        assert found_by_interval == sample_action


    def test_get_actions_in_str_format(self, action_array):
        """
        Test that getActionsInStrFormat() returns concatenated string of all Actions.
        The string may contain newlines if the Action body has preconditions/postconditions.
        """
        result = action_array.getActionsInStrFormat()
        # The Action identifier should be present
        assert "test_action" in result
        # Ensure the string ends properly, without extra trailing commas
        assert not result.endswith(",")


    def test_repr(self, action_array):
        """Test __repr__ of ActionArray for developer-friendly output."""
        r = repr(action_array)
        assert "ActionArray" in r
