# test_node.py
import pytest
from ..classes.node import Node, NodeArray, RangeTypes
from ..classes.element_types import ElementsTypes


# -----------------------------
# Dummy helpers (mocks)
# -----------------------------
class DummyUtils:
    def isNumericString(self, s):
        return s.isdigit()

    def containsOnlyPipe(self, s):
        return s == "|"


class DummyFormatter:
    def addEqueToBGET(self, s):
        return f"{s}_BGET"


# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def dummy_utils():
    return DummyUtils()


@pytest.fixture
def dummy_formatter():
    return DummyFormatter()


@pytest.fixture
def make_array(dummy_utils, dummy_formatter):
    """Factory for NodeArray with utils and formatter injected"""
    def _make(node_type=ElementsTypes.NONE_ELEMENT):
        arr = NodeArray(node_type)
        arr.utils = dummy_utils
        arr.string_formater = dummy_formatter
        return arr
    return _make


@pytest.fixture
def make_node():
    """Factory for Node with optional attributes"""
    def _make(identifier, etype=ElementsTypes.IDENTIFIER_ELEMENT, bit=False, rng=RangeTypes.UNDEFINED):
        n = Node(identifier, (0, 0), etype)
        n.bit_selection = bit
        n.range_selection = rng
        return n
    return _make


# -----------------------------
# RangeTypes tests
# -----------------------------
class TestRangeTypes:
    def test_rangetypes_values(self):
        assert set(RangeTypes) == {
            RangeTypes.START,
            RangeTypes.END,
            RangeTypes.UNDEFINED,
            RangeTypes.START_END,
        }


# -----------------------------
# Node tests
# -----------------------------
class TestNode:
    def test_node_init_defaults(self):
        ## Node should store its identifier by default
        n = Node("id")
        assert n.identifier == "id"

    def test_node_init_with_interval_and_type(self):
        ## Node should store provided source interval
        n = Node("id2", (1, 2), ElementsTypes.IDENTIFIER_ELEMENT)
        assert n.source_interval == (1, 2)

    def test_node_initialization_with_element_type(self):
        # Node should store provided element type
        node = Node("z", (0, 0), ElementsTypes.IDENTIFIER_ELEMENT)
        assert node.element_type == ElementsTypes.IDENTIFIER_ELEMENT

    def test_node_copy_creates_new_instance(self):
        # copy() should preserve attributes and return a new instance
        n = Node("sig")
        n.expression = "expr"
        n.design_unit_name = "DU"
        n.bit_selection = True
        n.range_selection = RangeTypes.START
        c = n.copy()
        assert (c.identifier, c.expression, c.design_unit_name, c.bit_selection, c.range_selection) == (
            "sig", "expr", "DU", True, RangeTypes.START
        )
        assert c is not n  # ensure it's a new object

    def test_node_getname_plain_identifier(self):
        # getName() should return identifier if nothing special is set
        node = Node("sig")
        assert node.getName() == "sig"

    def test_node_getname_with_design_unit(self):
        # getName() should prefix design_unit_name if it is set
        n = Node("b")
        n.design_unit_name = "U1"
        assert n.getName() == "U1.b"

    def test_node_getname_range_start_end(self):
        # START_END range should wrap identifier with parentheses
        n = Node("c")
        n.range_selection = RangeTypes.START_END
        assert n.getName() == "(c)"

    def test_node_getname_range_start(self):
        # START range should add "(" before identifier
        n = Node("d")
        n.range_selection = RangeTypes.START
        assert n.getName() == "(d"

    def test_node_getname_range_end(self):
        # END range should add ")" after identifier
        n = Node("e")
        n.range_selection = RangeTypes.END
        assert n.getName() == "e)"

    def test_node_str_returns_identifier(self):
        # __str__ should return identifier as string
        node = Node("test_id")
        assert str(node) == "test_id"

    def test_node_getname_with_bit_selection_and_numeric_utils(self, dummy_utils):
        # If bit_selection is True and identifier is numeric, wrap with parentheses
        n = Node("5")
        n.bit_selection = True
        n.utils = dummy_utils
        assert n.getName() == "(5)"

    def test_node_getname_with_bit_selection_non_numeric(self, dummy_utils):
        # If bit_selection is True and identifier is not numeric, prefix with comma
        n = Node("sig")
        n.bit_selection = True
        n.utils = dummy_utils
        assert n.getName() == ", sig)"

    def test_node_repr_includes_identifier(self):
        # __repr__ should include identifier for debugging
        n = Node("beta")
        rep = repr(n)
        assert "Node(identifier='beta'" in rep
        assert "element_type" in rep  # check more detail


# -----------------------------
# NodeArray tests
# -----------------------------
class TestNodeArray:
    def test_nodearray_init_sets_type(self):
        # Constructor should store provided node_type
        arr = NodeArray(ElementsTypes.IDENTIFIER_ELEMENT)
        assert arr.node_type == ElementsTypes.IDENTIFIER_ELEMENT

    def test_nodearray_is_assign_false_by_default(self, make_array):
        # By default isAssign() should return False 
        arr = make_array()
        assert arr.isAssign() is False

    def test_nodearray_is_assign_true_for_assign_element(self, make_array):
        # isAssign() should return True if action_type is ASSIGN_ELEMENT
        arr = make_array()
        arr.action_type = ElementsTypes.ASSIGN_ELEMENT
        assert arr.isAssign() is True

    def test_nodearray_add_element_appends_and_returns_index(self, make_array):
        # addElement() should append Node and return its index
        arr = make_array()
        n = Node("x")
        idx = arr.addElement(n)
        assert arr.getElementByIndex(idx) == n

    def test_nodearray_add_element_with_overlap(self, make_array):
        # If checkSourceInteval is False, addElement should return last index
        arr = make_array()
        n1 = Node("a", (1, 2))
        arr.addElement(n1)
        arr.checkSourceInteval = lambda x: False  # force overlap
        n2 = Node("b", (1, 2))
        idx = arr.addElement(n2)
        assert idx == 0

    def test_nodearray_get_element_by_index_out_of_bounds_raises(self, make_array):
        # getElementByIndex() should raise IndexError for invalid index
        arr = make_array()
        with pytest.raises(IndexError):
            arr.getElementByIndex(0)

    def test_nodearray_repr_contains_classname(self, make_array):
        # __repr__ should include class name "NodeArray"
        arr = make_array(ElementsTypes.IDENTIFIER_ELEMENT)
        assert "NodeArray(" in repr(arr)

    def test_nodearray_have_common_identifier_elements_true(self, make_array):
        # Two arrays with same identifier element should return True
        arr1 = make_array()
        arr2 = make_array()
        arr1.addElement(Node("same", element_type=ElementsTypes.IDENTIFIER_ELEMENT))
        arr2.addElement(Node("same", element_type=ElementsTypes.IDENTIFIER_ELEMENT))
        assert arr1.have_common_identifier_elements(arr2) is True

    def test_nodearray_have_common_identifier_elements_false(self, make_array):
        # Two arrays with different identifiers should return False
        arr1 = make_array()
        arr2 = make_array()
        arr1.addElement(Node("a", element_type=ElementsTypes.IDENTIFIER_ELEMENT))
        arr2.addElement(Node("b", element_type=ElementsTypes.IDENTIFIER_ELEMENT))
        assert arr1.have_common_identifier_elements(arr2) is False

    # -----------------------------
    # NodeArray.__str__ tests
    # -----------------------------
    def test_nodearray_str_basic_expression(self, make_array, make_node):
        # __str__ should render identifier + operator + number as "x + 1"
        arr = make_array()
        arr.addElement(make_node("x"))
        arr.addElement(make_node("+", ElementsTypes.OPERATOR_ELEMENT))
        arr.addElement(make_node("1", ElementsTypes.NUMBER_ELEMENT))
        assert str(arr) == "x + 1"

    def test_nodearray_str_with_unary_operator(self, make_array, make_node):
        # __str__ should render unary operator correctly, e.g. "!(y)"
        arr = make_array()
        arr.addElement(make_node("!", ElementsTypes.OPERATOR_ELEMENT))
        arr.addElement(make_node("y"))
        assert str(arr) == "!(y)"

    def test_nodearray_str_with_array_element(self, make_array, make_node):
        # ARRAY_ELEMENT should append ".value"
        arr = make_array()
        n = make_node("arr", ElementsTypes.ARRAY_ELEMENT)
        arr.addElement(n)
        assert str(arr) == "arr.value"

    def test_nodearray_str_with_array_size_element(self, make_array, make_node):
        # ARRAY_SIZE_ELEMENT should append ".size"
        arr = make_array()
        n = make_node("arr", ElementsTypes.ARRAY_SIZE_ELEMENT)
        arr.addElement(n)
        assert str(arr) == "arr.size"

    def test_nodearray_str_with_precondition_element(self, make_array, make_node):
        # PRECONDITION_ELEMENT should apply formatter (addEqueToBGET)
        arr = make_array(ElementsTypes.PRECONDITION_ELEMENT)
        n = make_node("cond")
        arr.addElement(n)
        assert str(arr) == "cond_BGET"

    def test_nodearray_str_with_pipe_after_operator(self, make_array, make_node):
        # "|" after operator should still render cleanly
        arr = make_array()
        arr.addElement(make_node("+", ElementsTypes.OPERATOR_ELEMENT))
        arr.addElement(make_node("|"))
        result = str(arr)
        assert " + " in result

    def test_nodearray_str_with_post_increment(self, make_array, make_node):
        # Post-increment "++" should render as "+ 1"
        arr = make_array()
        arr.addElement(make_node("x"))
        arr.addElement(make_node("++"))
        assert "= x + 1" in str(arr)

    def test_nodearray_str_with_post_decrement(self, make_array, make_node):
        # Post-decrement "--" should render as "- 1"
        arr = make_array()
        arr.addElement(make_node("x"))
        arr.addElement(make_node("--"))
        assert "= x - 1" in str(arr)

    def test_nodearray_str_empty(self, make_array):
        # An empty NodeArray should render as an empty string
        arr = make_array()
        assert str(arr) == ""
        