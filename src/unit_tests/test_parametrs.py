import pytest
from ..classes.parametrs import Parametr, ParametrArray


# ----------------------
# Tests for Parametr
# ----------------------
class TestParametr:
    def test_init_without_action_name(self):
        # When no action_name is given, unique_identifier should equal the identifier
        p = Parametr("WIDTH", "integer", (1, 10))
        assert p.identifier == "WIDTH"
        assert p.param_type == "integer"
        assert p.source_interval == (1, 10)
        assert p.unique_identifier == "WIDTH"
        assert p.design_unit_name is None

    def test_init_with_action_name(self):
        # unique_identifier should be correctly formed with action_name
        p = Parametr("data", "input", (5, 8), action_name="my_module")
        assert p.identifier == "data"
        assert p.param_type == "input"
        assert p.unique_identifier == "my_module_data"

    def test_copy(self):
        # Copy should create a new object with the same attributes but a different reference
        p = Parametr("clk", "logic")
        p.design_unit_name = "Top"
        p.number = 42
        clone = p.copy()
        assert clone.identifier == p.identifier
        assert clone.param_type == p.param_type
        assert clone.unique_identifier == p.unique_identifier
        assert clone.design_unit_name == "Top"
        assert clone.number == 42
        assert clone is not p  # ensure new object created

    def test_str_with_var_type(self):
        # If param_type contains "var", __str__ should only return the identifier
        p = Parametr("temp", "var")
        assert str(p) == "temp"

    def test_str_without_var_type(self):
        # Otherwise, __str__ should return "unique_identifier:param_type"
        p = Parametr("out", "output", action_name="unit")
        assert str(p) == "unit_out:output"

    def test_repr_contains_identifier(self):
        # __repr__ should contain detailed attributes including identifier
        p = Parametr("x", "integer")
        text = repr(p)
        assert "Parametr(" in text
        assert "identifier='x'" in text

    def test_repr_representation(self):
        p = Parametr("data", "output", source_interval=(50, 60))
        p.design_unit_name = "example_unit"
        expected_repr = (
            "Parametr(identifier='data', param_type='output', "
            "unique_identifier='data', source_interval=(50, 60), "
            "design_unit_name='example_unit', number=None)"
        )
        assert repr(p) == expected_repr

# ----------------------
# Tests for ParametrArray
# ----------------------
class TestParametrArray:
    # Fixture to initialize a fresh ParametrArray before each test
    @pytest.fixture(autouse=True)
    def setup_array(self):
        self.array = ParametrArray()

    def test_initialization(self):
        # A new ParametrArray should be empty and of correct type
        assert len(self.array) == 0
        assert self.array.element_type is Parametr

    def test_addElement_unique(self):
        # Adding a unique Parametr should return True and its index
        p = Parametr("a", "input")
        added, index = self.array.addElement(p)
        assert added is True
        assert index == 0
        assert self.array[0] == p

    def test_addElement_duplicate(self):
        # Adding a duplicate identifier should not insert a new element
        p1 = Parametr("a", "input")
        p2 = Parametr("a", "input")
        self.array.addElement(p1)
        added, index = self.array.addElement(p2)
        assert added is False
        assert index == 0
        assert len(self.array) == 1

    def test_addElement_wrong_type(self):
        # Adding anything other than Parametr should raise TypeError
        with pytest.raises(TypeError):
            self.array.addElement("not_a_parametr")  # type: ignore

    def test_copy_array(self):
        # Copy should return a deep copy of all elements
        p = Parametr("clk", "logic")
        self.array.addElement(p)
        clone = self.array.copy()
        assert isinstance(clone, ParametrArray)
        assert len(clone) == 1
        assert clone[0] is not p  # ensure new object
        assert clone[0].identifier == "clk"

    @pytest.mark.parametrize(
        "index,expected",
        [
            (0, "a"),
            (1, "b"),
            (25, "z"),
            (26, "aa"),
            (27, "ab"),
        ],
    )
    def test_generateParametrNameByIndex(self, index, expected):
        # Index should be converted to alphabetic names (Excel column style)
        assert self.array.generateParametrNameByIndex(index) == expected

    def test_getIdentifiersListString(self):
        # Should return identifiers in parentheses, comma-separated
        p1 = Parametr("p1", "input")
        p2 = Parametr("p2", "input")
        self.array.addElement(p1)
        self.array.addElement(p2)
        assert self.array.getIdentifiersListString(2) == "(p1, p2)"

    def test_getIdentifiersListString_empty(self):
        # Empty array should return an empty string
        assert self.array.getIdentifiersListString(0) == ""

    def test_getIdentifiersListString_too_many(self):
        # Asking for more identifiers than exist should raise ValueError
        p = Parametr("p", "input")
        self.array.addElement(p)
        with pytest.raises(ValueError):
            self.array.getIdentifiersListString(2)

    def test_generateUniqNamesForParamets(self):
        # Unique names should be assigned sequentially (a, b, c...)
        p1 = Parametr("x", "input")
        p2 = Parametr("y", "output")
        self.array.addElement(p1)
        self.array.addElement(p2)
        self.array.generateUniqNamesForParamets()
        assert p1.unique_identifier == "a"
        assert p2.unique_identifier == "b"

    def test_str_and_repr(self):
        # __str__ should join elements; __repr__ should include detailed info
        p1 = Parametr("a", "input")
        p2 = Parametr("b", "output")
        self.array.addElement(p1)
        self.array.addElement(p2)
        s = str(self.array)
        r = repr(self.array)
        assert "a:input" in s or "a" in s
        assert "ParametrArray" in r
        assert "Parametr(" in r
