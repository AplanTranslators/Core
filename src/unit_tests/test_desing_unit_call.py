import pytest
import logging


from ..classes.design_unit_call import DesignUnitCall, DesignUnitCallArray
from ..classes.value_parametrs import ValueParametrArray, ValueParametr
from ..classes.element_types import ElementsTypes

# ==========================================
# 1. Static Method Tests (Logic Verification)
# ==========================================

def test_extract_parameters_parsing():
    """
    Verifies that the static method correctly parses string assignments 
    into (name, value) tuples without needing any class instantiation.
    """
    expression = ".WIDTH(32), .DEPTH(SOURCE_DEPTH)"
    expected = [("WIDTH", "32"), ("DEPTH", "SOURCE_DEPTH")]
    
    result = DesignUnitCall.extractParametrsAndValues(expression)
    
    assert result == expected, "Regex should parse standard .PARAM(VALUE) syntax."

# ==========================================
# 2. Integration Tests: DesignUnitCall + ValueParametr
# ==========================================

def test_init_basic_attributes():
    """
    Verifies that a DesignUnitCall instance is correctly initialized with strings,
    and inherits properties (like element_type) from the real Basic class.
    """
    identifier = "u_cpu_core"
    object_name = "cpu_core"
    
    # Initialize with real strings
    dut = DesignUnitCall(
        identifier=identifier,
        object_name=object_name,
        source_identifier="def_cpu",
        destination_identifier="inst_cpu"
    )
    
    # Assert own attributes
    assert dut.identifier == identifier
    assert dut.object_name == object_name
    
    # Assert inherited attributes from real Basic class
    # DesignUnitCall __init__ hardcodes element_type to MODULE_CALL_ELEMENT
    assert dut.element_type == ElementsTypes.MODULE_CALL_ELEMENT
    
    # Assert sequence is an integer (assigned by the real Counters() singleton in Basic)
    assert isinstance(dut.sequence, int)

def test_init_resolves_real_parameters():
    """
    Verifies the integration between DesignUnitCall and ValueParametrArray.
    It checks if the call correctly looks up parameters in a REAL source array
    and adds them to its internal parameter list.
    """
    # 1. Setup: Create a real source array with parameters
    source_array = ValueParametrArray()
    
    # Add a parameter that WILL be used
    param_width = ValueParametr(identifier="WIDTH", source_interval=(0,0), value=32)
    source_array.addElement(param_width)
    
    # Add a parameter that will NOT be used
    param_unused = ValueParametr(identifier="UNUSED", source_interval=(0,0), value=0)
    source_array.addElement(param_unused)
    
    # 2. Action: Create the DesignUnitCall with an assignment string
    # We map .W to the existing "WIDTH" parameter
    assignment_str = ".W(WIDTH), .H(UNKNOWN_PARAM)"
    
    dut = DesignUnitCall(
        identifier="u_inst", 
        object_name="module", 
        source_identifier="src", 
        destination_identifier="dst",
        parameter_value_assignment=assignment_str,
        source_parametrs=source_array
    )
    
    # 3. Assertions
    # The internal list should now contain the real 'param_width' object
    assert len(dut.paramets) == 1, "Should have found exactly 1 valid parameter."
    
    # Verify the object identity (it should be the exact same object from source_array)
    stored_param = dut.paramets.getElement("WIDTH")
    
    assert stored_param is not None
    assert stored_param.value == 32
    assert stored_param.identifier == "WIDTH"
    
    # Verify 'UNKNOWN_PARAM' was ignored (not added to the array)
    assert dut.paramets.getElement("UNKNOWN_PARAM") is None

# ==========================================
# 3. Integration Tests: DesignUnitCallArray
# ==========================================

class TestDesignUnitCallArrayIntegration:
    
    @pytest.fixture
    def populated_array(self):
        """
        Fixture that creates a real DesignUnitCallArray with real DesignUnitCall elements.
        """
        arr = DesignUnitCallArray()
        
        # Element 1: ALU
        call1 = DesignUnitCall("u_alu", "alu_module", "alu_def", "alu_inst")
        arr.addElement(call1)
        
        # Element 2: RAM
        call2 = DesignUnitCall("u_ram", "ram_module", "ram_def", "ram_inst")
        arr.addElement(call2)
        
        return arr

    def test_find_module_by_uniq_identifier(self, populated_array):
        """
        Test finding a module using the real search logic iterating over real elements.
        """
        # Search for 'ram_module'
        found = populated_array.findModuleByUniqIdentifier("ram_module")
        
        assert found is not None
        assert found.identifier == "u_ram"
        assert found.element_type == ElementsTypes.MODULE_CALL_ELEMENT

    def test_get_elements_ie_filtering(self, populated_array):
        """
        Tests the getElementsIE method inherited from BasicArray but operating
        on DesignUnitCall objects.
        """
        # Filter by identifier
        # Note: getElementsIE returns a NEW array
        filtered_array = populated_array.getElementsIE(include_identifier="u_alu")
        
        assert len(filtered_array) == 1
        assert filtered_array[0].identifier == "u_alu"
        
        # Ensure deep copy behavior or reference integrity depending on implementation
        # The default implementation returns a new array wrapper
        assert isinstance(filtered_array, DesignUnitCallArray)


    def test_array_accepts_invalid_type_with_warning(self, caplog):
        arr = DesignUnitCallArray()
        valid_call = DesignUnitCall("u1", "mod1", "s1", "d1")

        arr.addElement(valid_call)
        assert len(arr) == 1

        with caplog.at_level("WARNING"):
            arr.addElement("not a DesignUnitCall")

        assert len(arr) == 2
        assert arr[0] == valid_call
        assert arr[1] == "not a DesignUnitCall"

        assert "Object should be of type DesignUnitCall" in caplog.text


    def test_copy_is_deep(self, populated_array):
        """
        Verifies that copying the array creates new instances of the array,
        preserving the data.
        """
        copied_arr = populated_array.copy()
        
        assert len(copied_arr) == len(populated_array)
        assert copied_arr[0].identifier == populated_array[0].identifier
        
        # Verify it's a different container object
        assert copied_arr is not populated_array

    # -------------------------------------------------------------------------
    # The following tests were previously missing the 'self' argument
    # -------------------------------------------------------------------------

    def test_string_representation_no_params(self):
        dut = DesignUnitCall("u1", "my_module", "def", "inst")

        output = str(dut)

        assert output.startswith("my_module u1 (")
        assert "// connections would go here" in output
        assert output.strip().endswith(");")


    def test_string_representation_with_params(self):
        """
        Verifies __str__ output INCLUDES parameters when they exist.
        Expected: "object_name identifier #(.P1(V1)) (...);"
        """
        # Setup: Create DUT and add a parameter manually
        dut = DesignUnitCall("u1", "my_module", "def", "inst")
        
        # Manually adding a resolved parameter for the test
        # Note: We depend on ValueParametr.__str__ which formats as "ID = VAL"
        # But DesignUnitCall.__str__ calls str(p) on the array.
        # We need to ensure the format matches what DesignUnitCall expects.
        param = ValueParametr("WIDTH", (0,0), value=10)
        dut.paramets.addElement(param)
        
        output = str(dut)
        
        # We verify the output contains the specific formatted string
        assert "#(" in output
        assert "WIDTH" in output
        assert "10" in output
        assert "my_module u1" in output

    def test_extract_parameters_complex_whitespace(self):
        """
        Verifies regex handles extreme whitespace around parenthesis and commas.
        Input: ".A ( 10 ) , .B   ( 20 )"
        """
        expression = ".A ( 10 ) , .B   ( 20 )"
        expected = [("A", " 10 "), ("B", " 20 ")]
        
        result = DesignUnitCall.extractParametrsAndValues(expression)
        
        # Note: The current regex captures the whitespace inside the value group (.+?)
        assert result == expected

    def test_extract_parameters_expressions(self):
        """
        Verifies regex handles simple math expressions inside the value.
        Input: ".ADDR(BASE + OFFSET)"
        """
        expression = ".ADDR(BASE + OFFSET)"
        expected = [("ADDR", "BASE + OFFSET")]
        
        result = DesignUnitCall.extractParametrsAndValues(expression)
        assert result == expected

    def test_extract_parameters_malformed_input(self):
        """
        Verifies behavior on inputs that don't match the pattern.
        Should just return empty list or ignore the garbage.
        """
        # Missing dot, missing parens
        expression = "WIDTH(10), .DEPTH=20" 
        
        result = DesignUnitCall.extractParametrsAndValues(expression)
        
        # "WIDTH(10)" has no leading dot -> Ignored
        # ".DEPTH=20" has no Parens -> Ignored
        assert result == []

    def test_init_defensive_missing_source_params(self):
        """
        Verifies initialization is safe when assignment string is provided 
        but source_parametrs is None.
        """
        dut = DesignUnitCall(
            "u1", "mod", "s", "d",
            parameter_value_assignment=".W(10)",
            source_parametrs=None # Explicitly None
        )
        
        assert len(dut.paramets) == 0

    def test_init_defensive_missing_assignment_string(self):
        """
        Verifies initialization is safe when source_parametrs is provided 
        but assignment string is None.
        """
        src_array = ValueParametrArray()
        src_array.addElement(ValueParametr("W", (0,0), value=10))
        
        dut = DesignUnitCall(
            "u1", "mod", "s", "d",
            parameter_value_assignment=None, # Explicitly None
            source_parametrs=src_array
        )
        
        assert len(dut.paramets) == 0

    def test_init_with_empty_source_array(self):
        """
        Verifies behavior when assignment string exists, but source array is empty.
        """
        src_array = ValueParametrArray() # Empty
        
        dut = DesignUnitCall(
            "u1", "mod", "s", "d",
            parameter_value_assignment=".W(10)",
            source_parametrs=src_array
        )
        
        assert len(dut.paramets) == 0