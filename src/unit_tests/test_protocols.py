import pytest
import re
from ..classes.protocols import BodyElement, BodyElementArray, Protocol, ProtocolArray
from ..classes.element_types import ElementsTypes
from ..classes.parametrs import ParametrArray


# ==========================================================
# Tests for BodyElement
# ==========================================================

class TestBodyElement:
    """Unit tests for the BodyElement class."""

    def test_initialization_defaults(self):
        """BodyElement should initialize with default parameters."""
        elem = BodyElement("test_elem")
        assert elem.identifier == "test_elem"
        assert isinstance(elem.parametrs, ParametrArray)
        assert elem.pointer_to_related is None
        assert elem.element_type == ElementsTypes.NONE_ELEMENT

    def test_initialization_with_params_and_pointer(self):
        """BodyElement should accept custom parameters and related pointer."""
        params = ParametrArray()
        related = BodyElement("related_elem")
        elem = BodyElement(
            "test_elem",
            pointer_to_related=related,
            element_type=ElementsTypes.NONE_ELEMENT,
            parametrs=params
        )

        assert elem.identifier == "test_elem"
        assert elem.pointer_to_related == related
        assert elem.element_type == ElementsTypes.NONE_ELEMENT
        assert elem.parametrs == params

    def test_copy_creates_independent_copy(self):
        """Copy should create a new independent BodyElement with same attributes."""
        elem = BodyElement("test_elem")
        copy_elem = elem.copy()
        assert copy_elem is not elem
        assert copy_elem.identifier == elem.identifier
        assert copy_elem.parametrs is not elem.parametrs
        assert copy_elem.element_type == elem.element_type

    def test_getName_with_and_without_params(self):
        """getName should return identifier with or without parameter list."""
        elem_no_params = BodyElement("elem_no_params")
        assert elem_no_params.getName() == "elem_no_params"

        params = ParametrArray()
        elem_with_params = BodyElement("elem_with_params", parametrs=params)
        assert elem_with_params.getName() == "elem_with_params"


    def test_str_and_repr(self):
        """__str__ should return getName, and __repr__ should show key attributes."""
        elem = BodyElement("my_elem")
        assert str(elem) == "my_elem"
        rep = repr(elem)
        assert "BodyElement(" in rep
        assert "my_elem" in rep

    def test_copy_with_pointer_to_related_bodyelement(self):
        """copy() should deep-copy pointer_to_related if it's another BodyElement."""
        related = BodyElement("related")
        elem = BodyElement("main", pointer_to_related=related)
        copy_elem = elem.copy()
        assert copy_elem.pointer_to_related is not related
        assert copy_elem.pointer_to_related.identifier == "related"

    def test_copy_with_pointer_to_related_bodyelementarray(self):
        """copy() should deep-copy pointer_to_related if it's a BodyElementArray."""
        arr = BodyElementArray()
        arr.addElement(BodyElement("nested"))
        elem = BodyElement("main", pointer_to_related=arr)
        copy_elem = elem.copy()
        assert isinstance(copy_elem.pointer_to_related, BodyElementArray)
        assert copy_elem.pointer_to_related is not arr
        assert copy_elem.pointer_to_related[0].identifier == "nested"


# ==========================================================
# Tests for BodyElementArray
# ==========================================================

class TestBodyElementArray:
    """Unit tests for the BodyElementArray class."""

    def test_add_and_len(self):
        """addElement should add a BodyElement and increase length."""
        array = BodyElementArray()
        elem = BodyElement("elem1")
        index = array.addElement(elem)
        assert index == 0
        assert len(array) == 1

    def test_getitem_and_iteration(self):
        """Array should support indexing and iteration."""
        array = BodyElementArray()
        elems = [BodyElement(f"elem{i}") for i in range(3)]
        for e in elems:
            array.addElement(e)

        # Indexing
        assert array[0] == elems[0]
        assert array[1:3] == elems[1:3]

        # Iteration
        collected = [e for e in array]
        assert collected == elems

    def test_copy_creates_independent_copy(self):
        """Copy should create new array with deep-copied elements."""
        array = BodyElementArray()
        elem = BodyElement("elem1")
        array.addElement(elem)
        copy_array = array.copy()
        assert copy_array is not array
        assert copy_array.elements[0] is not elem
        assert copy_array.elements[0].identifier == elem.identifier

    def test_toStr_empty_and_single(self):
        """toStr() should return an empty string for no elements and a correctly formatted
        string with a trailing comma for a single element."""
        arr = BodyElementArray()
        assert arr.toStr() == ""
        arr.addElement(BodyElement("single"))
        assert arr.toStr() == "single,"

    def test_toStr_separators_and_forever(self):
        """toStr() should insert a semicolon before a FOREVER block and a trailing comma
        at the end."""
        arr = BodyElementArray()
        arr.addElement(BodyElement("first"))
        arr.addElement(BodyElement("second", element_type=ElementsTypes.FOREVER_ELEMENT))
        s = arr.toStr()
        assert s == "first;{second},"

        arr2 = BodyElementArray(element_type=ElementsTypes.GENERATE_ELEMENT)
        arr2.addElement(BodyElement("a"))
        arr2.addElement(BodyElement("b"))
        assert arr2.toStr() == "a || b,"

    def test_toStr_if_condition_group(self):
        """toStr() should wrap IF_CONDITION_LEFT/RIGHT in parentheses with plus sign."""
        arr = BodyElementArray()
        arr.addElement(BodyElement("cond1", element_type=ElementsTypes.IF_CONDITION_LEFT))
        arr.addElement(BodyElement("cond2", element_type=ElementsTypes.IF_CONDITION_RIGTH))
        s = arr.toStr()
        assert "(cond1" in s
        assert "+ cond2" in s
        assert ")" in s

    def test_toStr_last_comma_false(self):
        """toStr(last_comma=False) should not append trailing comma."""
        arr = BodyElementArray()
        arr.addElement(BodyElement("elem"))
        s = arr.toStr(last_comma=False)
        assert not s.endswith(",")


# ==========================================================
# Tests for Protocol
# ==========================================================

class DummyUtils:
    """Stub for utils with extractFunctionName."""
    def extractFunctionName(self, identifier):
        return identifier

class DummyDesignUnit:
    """Stub for design_unit with actions collection."""
    def __init__(self, action):
        self.actions = ProtocolArray()
        self.actions.addElement(action)

class TestProtocol:
    """Unit tests for the Protocol class."""

    def test_initialization_defaults(self):
        """Protocol should initialize with default values and structures."""
        proto = Protocol("proto1", (0, 10))
        assert proto.identifier == "proto1"
        assert proto.source_interval == (0, 10)
        assert isinstance(proto.body, BodyElementArray)
        assert isinstance(proto.parametrs, ParametrArray)
        assert proto.element_type == ElementsTypes.NONE_ELEMENT

    def test_copy_creates_independent_copy(self):
        """Copy should create independent Protocol with copied body elements."""
        proto = Protocol("proto1", (0, 10))
        elem = BodyElement("elem1")
        proto.addBodyElement(elem)

        copy_proto = proto.copy()
        assert copy_proto is not proto
        assert copy_proto.identifier == proto.identifier
        assert copy_proto.source_interval == proto.source_interval
        assert copy_proto.body.elements[0] is not proto.body.elements[0]
        assert copy_proto.body.elements[0].identifier == elem.identifier

    def test_getName_with_number_and_params(self):
        """getName should reflect number and parameters when present."""
        proto = Protocol("proto1", (0, 10))
        proto.number = 1
        assert proto.getName() == "proto1_1"

        proto.parametrs = ParametrArray()
        assert proto.getName() == "proto1_1"

    def test_addBodyElement_adds_to_body(self):
        """addBodyElement should append element to body array."""
        proto = Protocol("proto1", (0, 10))
        elem = BodyElement("elem1")
        proto.addBodyElement(elem)
        assert proto.body.elements[0] == elem

    def test_str_and_repr(self):
        """__str__ should return getName, and __repr__ should show key attributes."""
        proto = Protocol("protoX", (1, 2))
        s = str(proto)
        rep = repr(proto)
        assert "protoX" in s
        assert "Protocol(" in rep

    def test_getName_number_zero_and_none(self):
        """getName should behave differently for number=None vs number=0."""
        proto = Protocol("protoZ", (0, 1))
        assert proto.getName() == "protoZ"
        proto.number = 0
        assert proto.getName() == "protoZ_0"

    def test_updateLinks_exposes_vulnerability_replaces_with_tuple(self):
        """
        This test exposes a vulnerability: the updateLinks method
        replaces a BodyElement with a tuple instead of updating pointer_to_related.
        """
        # Setup mock objects
        action_object = Protocol("my_action", (0, 1))
        proto = Protocol("main_proto", (0, 5))
        body_element = BodyElement("my_action")
        proto.addBodyElement(body_element)

        # Mock design unit
        class DummyDesignUnit:
            def __init__(self, actions):
                self.actions = ProtocolArray()
                self.actions.addElement(actions)

        design_unit = DummyDesignUnit(action_object)

        # Mock utils
        class DummyUtils:
            def extractFunctionName(self, identifier):
                return identifier

        proto.utils = DummyUtils()

        # Call the method
        proto.updateLinks(design_unit)

        # Checks: the element is now a tuple
        assert isinstance(proto.body[0], tuple)
        assert proto.body[0][0] is action_object
        assert not isinstance(proto.body[0], BodyElement)

    @pytest.mark.xfail(reason="updateLinks currently replaces BodyElement with tuple instead of updating pointer_to_related")
    def test_updateLinks_updates_pointer_correctly(self):
        """
        This test describes the correct logic: the method should
        keep the BodyElement and update its pointer_to_related.
        """
        # Setup mock objects
        action_object = Protocol("my_action", (0, 1))
        proto = Protocol("main_proto", (0, 5))
        body_element = BodyElement("my_action")
        proto.addBodyElement(body_element)

        # Mock design unit
        class DummyDesignUnit:
            def __init__(self, actions):
                self.actions = ProtocolArray()
                self.actions.addElement(actions)

        design_unit = DummyDesignUnit(action_object)

        # Call the method
        proto.updateLinks(design_unit)

        # Expected (but currently not implemented) behavior
        assert isinstance(proto.body[0], BodyElement)
        assert proto.body[0].pointer_to_related is action_object

    

# ==========================================================
# Tests for ProtocolArray
# ==========================================================

class DummyStringFormatter:
    def removeTrailingComma(self, text: str) -> str:
        return re.sub(r",\s*$", "", text, flags=re.MULTILINE)

class TestProtocolArray:
    """Unit tests for the ProtocolArray class."""

    def test_add_and_len(self):
        """addElement should add a Protocol and increase length."""
        array = ProtocolArray()
        proto = Protocol("p1", (0, 1))
        array.addElement(proto)
        assert len(array) == 1
        assert array[0] == proto

    def test_copy_creates_independent_copy(self):
        """Copy should create new array with copied Protocol objects."""
        array = ProtocolArray()
        proto = Protocol("p1", (0, 1))
        array.addElement(proto)

        copy_array = array.copy()
        assert copy_array is not array
        assert copy_array.elements[0] is not proto
        assert copy_array.elements[0].identifier == proto.identifier

    def test_getElementsIE_filters_correctly(self):
        """getElementsIE should include or exclude protocols by type or identifier."""
        array = ProtocolArray()
        proto1 = Protocol("p1", (0, 1))
        proto2 = Protocol("p2", (0, 2))
        proto2.element_type = ElementsTypes.FOREVER_ELEMENT
        array.addElement(proto1)
        array.addElement(proto2)

        # Include filter
        included = array.getElementsIE(include_type=ElementsTypes.FOREVER_ELEMENT)
        assert len(included) == 1
        assert included[0] == proto2

        # Exclude filter
        excluded = array.getElementsIE(exclude_identifier="p1")
        assert len(excluded) == 1
        assert excluded[0] == proto2

    def test_getElementsIE_combined_filters(self):
        array = ProtocolArray()
        proto1 = Protocol("p1", (0, 1))  # NONE_ELEMENT
        proto2 = Protocol("p2", (0, 2), element_type=ElementsTypes.FOREVER_ELEMENT)
        proto3 = Protocol("excluded", (0, 3), element_type=ElementsTypes.FOREVER_ELEMENT)
        array.addElement(proto1)
        array.addElement(proto2)
        array.addElement(proto3)
        filtered = array.getElementsIE(include_type=ElementsTypes.FOREVER_ELEMENT, exclude_identifier="excluded")
        expected_count = 1  # Only proto2 passes both filters
        assert len(filtered) == expected_count

    def test_str_and_repr(self):
        """__str__ should list protocols, and __repr__ should show class name."""
        array = ProtocolArray()
        p = Protocol("p", (0, 1))
        array.addElement(p)
        s = str(array)
        rep = repr(array)
        assert "p" in s
        assert "ProtocolsArray" in rep

    def test_getProtocolsInStrFormat_with_string_formatter(self):
        """getProtocolsInStrFormat should remove trailing commas when string_formater is set."""
        array = ProtocolArray()
        proto = Protocol("protoX", (0, 1))
        array.addElement(proto)
        array.string_formater = DummyStringFormatter()

        s = array.getProtocolsInStrFormat()
        assert not s.endswith(",")

    def test_updateLinks_delegates_to_protocols(self):
        """updateLinks should call updateLinks on each Protocol."""
        array = ProtocolArray()
        proto = Protocol("protoY", (0, 1))
        proto.utils = DummyUtils()
        proto2 = Protocol("actionProto", (0, 2))
        proto.addBodyElement(BodyElement("actionProto"))
        array.addElement(proto)
        array.addElement(proto2)

        design_unit = DummyDesignUnit(proto2)
        array.updateLinks(design_unit)
        assert isinstance(proto.body.elements[0], tuple)

    def test_empty_protocolarray_returns_empty_string(self):
        """Empty ProtocolArray should return empty string."""
        array = ProtocolArray()
        assert array.getProtocolsInStrFormat() == ""