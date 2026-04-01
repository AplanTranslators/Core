"""
Unit tests for ValueParametr and ValueParametrArray.

Dependencies (Basic, BasicArray, ElementsTypes, StringFormater, UnsortedUnils,
Counters, Logger) are exercised through their real implementations, which are
already available as class-level attributes on Basic / BasicArray.
"""

import pytest
from ..classes.value_parametrs import ValueParametr, ValueParametrArray
from ..classes.element_types import ElementsTypes
from ..classes.basic import Basic


# ===========================================================================
# Helpers
# ===========================================================================

def make_vp(identifier="X", source_interval=(0, 0), value=0, expression=None):
    """Factory shorthand to keep test bodies concise."""
    return ValueParametr(identifier, source_interval, value, expression)


def make_array(*params: ValueParametr) -> ValueParametrArray:
    """Build a ValueParametrArray from a sequence of ValueParametr objects."""
    arr = ValueParametrArray()
    for p in params:
        arr.addElement(p)
    return arr


# ===========================================================================
# 1. ValueParametr – __init__
# ===========================================================================

class TestValueParametrInit:

    def test_identifier_is_stored(self):
        vp = make_vp("WIDTH")
        assert vp.identifier == "WIDTH"

    def test_source_interval_is_stored(self):
        vp = make_vp(source_interval=(3, 17))
        assert vp.source_interval == (3, 17)

    def test_default_value_is_zero(self):
        vp = make_vp()
        assert vp.value == 0

    def test_custom_value_is_stored(self):
        vp = make_vp(value=42)
        assert vp.value == 42

    def test_default_expression_is_none(self):
        vp = make_vp()
        assert vp.expression is None

    def test_custom_expression_is_stored(self):
        vp = make_vp(expression="A + B")
        assert vp.expression == "A + B"

    def test_element_type_defaults_to_none_element(self):
        vp = make_vp()
        assert vp.element_type is ElementsTypes.NONE_ELEMENT

    def test_number_defaults_to_none(self):
        vp = make_vp()
        assert vp.number is None

    def test_inherits_from_basic(self):
        vp = make_vp()
        assert isinstance(vp, Basic)


# ===========================================================================
# 2. ValueParametr – copy()
# ===========================================================================

class TestValueParametrCopy:

    def test_copy_returns_different_object(self):
        vp = make_vp("A", (0, 0), 10, "5+5")
        assert vp.copy() is not vp

    def test_copy_preserves_identifier(self):
        vp = make_vp("A")
        assert vp.copy().identifier == "A"

    def test_copy_preserves_source_interval(self):
        vp = make_vp(source_interval=(1, 9))
        assert vp.copy().source_interval == (1, 9)

    def test_copy_preserves_value(self):
        vp = make_vp(value=7)
        assert vp.copy().value == 7

    def test_copy_preserves_expression(self):
        vp = make_vp(expression="X*2")
        assert vp.copy().expression == "X*2"

    def test_copy_preserves_number_when_set(self):
        vp = make_vp()
        vp.number = 99
        assert vp.copy().number == 99

    def test_copy_preserves_number_none(self):
        vp = make_vp()
        assert vp.copy().number is None

    def test_copy_value_mutation_does_not_affect_original(self):
        vp = make_vp(value=5)
        copied = vp.copy()
        copied.value = 999
        assert vp.value == 5

    def test_copy_returns_value_parametr_instance(self):
        vp = make_vp()
        assert isinstance(vp.copy(), ValueParametr)


# ===========================================================================
# 3. ValueParametr – prepareExpression()
# ===========================================================================

class TestValueParametrPrepareExpression:

    def test_none_expression_stays_none(self):
        vp = make_vp(expression=None)
        vp.prepareExpression()
        assert vp.expression is None


    def test_prepare_expression_with_string_formater_none_leaves_expression_unchanged(self):
        """
        When string_formater is explicitly set to None on the instance,
        prepareExpression must exit early without modifying the expression.
        """
        vp = make_vp(expression="A+B")
        vp.string_formater = None          # shadow the class attribute
        vp.prepareExpression()
        assert vp.expression == "A+B"

    def test_prepare_expression_with_string_formater_none_logs_warning(self, caplog):
        import logging
        vp = make_vp("MYVAR", expression="A+B")
        vp.string_formater = None
        with caplog.at_level(logging.WARNING):
            vp.prepareExpression()
        assert any(
            "not available" in r.message and "MYVAR" in r.message
            for r in caplog.records
        )


# ===========================================================================
# 4. ValueParametr – __str__
# ===========================================================================

class TestValueParametrStr:

    def test_str_uses_expression_when_present(self):
        vp = make_vp("W", value=32, expression="16*2")
        assert str(vp) == "W = 16*2"

    def test_str_uses_value_when_expression_is_none(self):
        vp = make_vp("W", value=32, expression=None)
        assert str(vp) == "W = 32"

    def test_str_uses_value_when_expression_is_empty_string(self):
        """Empty string is falsy; __str__ should fall back to value."""
        vp = make_vp("W", value=7, expression="")
        assert str(vp) == "W = 7"


# ===========================================================================
# 5. ValueParametr – __repr__
# ===========================================================================

class TestValueParametrRepr:

    def test_repr_contains_class_name(self):
        assert "ValueParametr(" in repr(make_vp("A"))

    def test_repr_contains_identifier(self):
        assert "'A'" in repr(make_vp("A"))

    def test_repr_contains_value(self):
        assert "5" in repr(make_vp(value=5))

    def test_repr_contains_expression(self):
        assert "'E'" in repr(make_vp(expression="E"))

    def test_repr_contains_source_interval(self):
        assert "(1, 2)" in repr(make_vp(source_interval=(1, 2)))


# ===========================================================================
# 6. ValueParametrArray – __init__
# ===========================================================================

class TestValueParametrArrayInit:

    def test_element_type_is_value_parametr(self):
        assert ValueParametrArray().element_type is ValueParametr

    def test_starts_empty(self):
        assert len(ValueParametrArray()) == 0

    def test_inherits_from_basic_array(self):
        from ..classes.basic import BasicArray
        assert isinstance(ValueParametrArray(), BasicArray)


# ===========================================================================
# 7. ValueParametrArray – addElement()
# ===========================================================================

class TestValueParametrArrayAddElement:

    def test_raises_type_error_for_wrong_type(self):
        arr = ValueParametrArray()
        with pytest.raises(TypeError):
            arr.addElement("not_a_value_parametr")

    def test_raises_type_error_for_basic_instance(self):
        arr = ValueParametrArray()
        with pytest.raises(TypeError):
            arr.addElement(Basic("b", (0, 0)))

    def test_type_error_message_mentions_value_parametr(self):
        arr = ValueParametrArray()
        with pytest.raises(TypeError, match="ValueParametr"):
            arr.addElement(42)

    def test_element_is_present_after_add(self):
        arr = ValueParametrArray()
        vp = make_vp("A")
        arr.addElement(vp)
        assert any(e.identifier == "A" for e in arr)

    def test_length_increases_after_add(self):
        arr = ValueParametrArray()
        arr.addElement(make_vp("A"))
        assert len(arr) == 1

    def test_longer_identifier_matched_before_shorter_substring(self):
        """
        Behavioral contract: when one identifier is a prefix of another
        (e.g. "WIDTH" vs "WIDTH_MAX"), the longer one must be substituted
        first so that "WIDTH_MAX" is not corrupted into "8_MAX".
        We verify this by checking that both identifiers survive in the array
        and that the longer one can be retrieved without ambiguity.
        """
        arr = make_array(make_vp("WIDTH"), make_vp("WIDTH_MAX"))
        identifiers = [e.identifier for e in arr]
        assert "WIDTH_MAX" in identifiers
        assert "WIDTH" in identifiers
        assert arr[0].identifier == "WIDTH_MAX"
        # The longer identifier must appear before the shorter one
        assert identifiers.index("WIDTH_MAX") < identifiers.index("WIDTH")

    def test_returned_index_is_correct_after_sort(self):
        arr = ValueParametrArray()
        arr.addElement(make_vp("A"))
        idx = arr.addElement(make_vp("LONGNAME"))
        assert arr[idx].identifier == "LONGNAME"

    def test_prepareExpression_called_on_element_transforms_expression(self):
        """
        addElement must call prepareExpression on the new element.
        We verify this by supplying a C-style '!0' expression: the real
        pipeline rewrites it, so if prepareExpression ran the stored
        expression must differ from the original raw input.
        """
        vp = make_vp("A", expression="!0")
        arr = ValueParametrArray()
        arr.addElement(vp)
        assert vp.expression != "!0"

    def test_duplicate_identifiers_are_allowed(self):
        arr = ValueParametrArray()
        arr.addElement(make_vp("DUP"))
        arr.addElement(make_vp("DUP"))
        assert len(arr) == 2

    def test_get_element_index_returns_first_match_for_duplicates(self):
        """
        getElementIndex scans linearly and returns the first match.
        With two elements sharing the same identifier, it must return
        index 0 (the first occurrence in sorted order), not index 1.
        """
        arr = ValueParametrArray()
        arr.addElement(make_vp("DUP"))
        arr.addElement(make_vp("DUP"))
        assert arr.getElementIndex("DUP") == 0


# ===========================================================================
# 8. ValueParametrArray – copy()
# ===========================================================================

class TestValueParametrArrayCopy:

    def test_copy_returns_different_array_object(self):
        arr = make_array(make_vp("A"))
        assert arr.copy() is not arr

    def test_copy_contains_same_number_of_elements(self):
        arr = make_array(make_vp("A"), make_vp("BB"))
        assert len(arr.copy()) == 2

    def test_copy_element_is_different_object(self):
        vp = make_vp("A")
        arr = make_array(vp)
        assert arr.copy()[0] is not vp

    def test_copy_mutation_does_not_affect_original(self):
        arr = make_array(make_vp("A", value=1))
        copied = arr.copy()
        copied[0].value = 999
        assert arr[0].value == 1

    def test_copy_returns_value_parametr_array_instance(self):
        arr = make_array(make_vp("A"))
        assert isinstance(arr.copy(), ValueParametrArray)

    def test_copy_of_empty_array_is_empty(self):
        assert len(ValueParametrArray().copy()) == 0


# ===========================================================================
# 9. ValueParametrArray – getElementByIndex()
# ===========================================================================

class TestValueParametrArrayGetElementByIndex:

    def test_retrieves_element_at_index_zero(self):
        arr = make_array(make_vp("LONG"), make_vp("A"))
        # After sort: LONG is at 0
        assert arr.getElementByIndex(0).identifier == "LONG"

    def test_raises_index_error_for_empty_array(self):
        with pytest.raises(IndexError):
            ValueParametrArray().getElementByIndex(0)

    def test_raises_index_error_for_out_of_bounds(self):
        arr = make_array(make_vp("A"))
        with pytest.raises(IndexError):
            arr.getElementByIndex(99)

    def test_returns_value_parametr_instance(self):
        arr = make_array(make_vp("A"))
        assert isinstance(arr.getElementByIndex(0), ValueParametr)


# ===========================================================================
# 10. ValueParametrArray – getElementsIE()
# ===========================================================================

class TestValueParametrArrayGetElementsIE:

    @pytest.fixture
    def two_element_array(self):
        vp1 = make_vp("PARAM_A")
        vp1.element_type = ElementsTypes.NUMBER_ELEMENT
        vp2 = make_vp("PARAM_B")
        vp2.element_type = ElementsTypes.IDENTIFIER_ELEMENT
        return make_array(vp1, vp2)

    # --- no filters ---

    def test_no_filters_returns_value_parametr_array(self, two_element_array):
        assert isinstance(two_element_array.getElementsIE(), ValueParametrArray)

    def test_no_filters_returns_all_elements(self, two_element_array):
        assert len(two_element_array.getElementsIE()) == 2

    def test_no_filters_returns_new_object(self, two_element_array):
        assert two_element_array.getElementsIE() is not two_element_array

    # --- include_type ---

    def test_include_type_returns_matching_element(self, two_element_array):
        res = two_element_array.getElementsIE(include_type=ElementsTypes.NUMBER_ELEMENT)
        assert any(p.identifier == "PARAM_A" for p in res)

    def test_include_type_excludes_non_matching_element(self, two_element_array):
        res = two_element_array.getElementsIE(include_type=ElementsTypes.NUMBER_ELEMENT)
        assert not any(p.identifier == "PARAM_B" for p in res)

    def test_include_type_result_length(self, two_element_array):
        res = two_element_array.getElementsIE(include_type=ElementsTypes.NUMBER_ELEMENT)
        assert len(res) == 1

    # --- exclude_type ---

    def test_exclude_type_removes_matching_element(self, two_element_array):
        res = two_element_array.getElementsIE(exclude_type=ElementsTypes.NUMBER_ELEMENT)
        assert not any(p.identifier == "PARAM_A" for p in res)

    def test_exclude_type_keeps_non_matching_element(self, two_element_array):
        res = two_element_array.getElementsIE(exclude_type=ElementsTypes.NUMBER_ELEMENT)
        assert any(p.identifier == "PARAM_B" for p in res)

    # --- include_identifier ---

    def test_include_identifier_returns_only_matching(self, two_element_array):
        res = two_element_array.getElementsIE(include_identifier="PARAM_A")
        assert len(res) == 1

    def test_include_identifier_correct_element(self, two_element_array):
        res = two_element_array.getElementsIE(include_identifier="PARAM_A")
        assert res[0].identifier == "PARAM_A"

    # --- exclude_identifier ---

    def test_exclude_identifier_removes_matching(self, two_element_array):
        res = two_element_array.getElementsIE(exclude_identifier="PARAM_A")
        assert not any(p.identifier == "PARAM_A" for p in res)

    def test_exclude_identifier_keeps_other(self, two_element_array):
        res = two_element_array.getElementsIE(exclude_identifier="PARAM_A")
        assert any(p.identifier == "PARAM_B" for p in res)

    # --- combined filters ---

    def test_combined_include_type_and_exclude_identifier(self, two_element_array):
        """include NUMBER_ELEMENT but also exclude PARAM_A → empty result."""
        res = two_element_array.getElementsIE(
            include_type=ElementsTypes.NUMBER_ELEMENT,
            exclude_identifier="PARAM_A",
        )
        assert len(res) == 0

    def test_combined_include_identifier_and_exclude_type_no_match(self, two_element_array):
        """include PARAM_A but exclude NUMBER_ELEMENT → empty (PARAM_A IS NUMBER_ELEMENT)."""
        res = two_element_array.getElementsIE(
            include_identifier="PARAM_A",
            exclude_type=ElementsTypes.NUMBER_ELEMENT,
        )
        assert len(res) == 0

    # --- object identity: filtered path returns same objects, no-filter path returns copies ---

    def test_filter_with_criteria_returns_same_objects(self, two_element_array):
        """
        When at least one filter is active, getElementsIE does addElement(element)
        without copying — so the objects in the result must be the exact same
        instances as in the original array, not copies.
        """
        res = two_element_array.getElementsIE(include_identifier="PARAM_A")
        original = next(e for e in two_element_array if e.identifier == "PARAM_A")
        assert res[0] is original

    def test_no_filter_returns_copies_not_same_objects(self, two_element_array):
        """
        The no-filter path calls self.copy(), which creates new ValueParametr
        instances — so elements in the result must NOT be the same objects.
        """
        res = two_element_array.getElementsIE()
        original = two_element_array[0]
        assert res[0] is not original

    # --- empty array edge case ---

    def test_filter_on_empty_array_returns_empty(self):
        arr = ValueParametrArray()
        res = arr.getElementsIE(include_type=ElementsTypes.NUMBER_ELEMENT)
        assert len(res) == 0


# ===========================================================================
# 11. ValueParametrArray – evaluateParametrExpressionByIndex()
# ===========================================================================

class TestValueParametrArrayEvaluate:

    def test_returns_value_when_expression_is_none(self):
        arr = make_array(make_vp("A", value=99, expression=None))
        assert arr.evaluateParametrExpressionByIndex(0) == 99

    def test_returns_value_when_expression_is_empty(self):
        arr = make_array(make_vp("A", value=55, expression=""))
        assert arr.evaluateParametrExpressionByIndex(0) == 55

    def test_raises_index_error_for_out_of_bounds(self):
        arr = ValueParametrArray()
        with pytest.raises(IndexError):
            arr.evaluateParametrExpressionByIndex(0)

    def test_evaluated_value_is_stored_on_parametr(self):
        """
        Uses real string_formater + utils available via class attributes.
        Expression "2 + 3" should evaluate to 5 and be stored back.
        """
        vp = make_vp("A", expression="2 + 3")
        arr = make_array(vp)
        idx = arr.getElementIndex("A")
        arr.evaluateParametrExpressionByIndex(idx)
        assert vp.value == 5

    def test_identifier_collision_longer_first(self):
        """
        Critical case: identifiers where one is a prefix of another.

        A = 1
        AA = 10
        expression = "AA + A"

        Must evaluate as: 10 + 1 = 11
        NOT: "1A + 1" or other corrupted substitutions.
        """
        vp_a = make_vp("A", value=1)
        vp_aa = make_vp("AA", value=10)
        vp_expr = make_vp("X", expression="AA + A")

        arr = make_array(vp_a, vp_aa, vp_expr)

        idx = arr.getElementIndex("X")
        result = arr.evaluateParametrExpressionByIndex(idx)

        assert result == 11

    def test_identifier_collision_order_independent(self):
        """
        Order of insertion must not affect correctness.
        """
        vp_aa = make_vp("AA", value=10)
        vp_a = make_vp("A", value=1)
        vp_expr = make_vp("X", expression="AA + A")

        arr = make_array(vp_aa, vp_a, vp_expr)

        idx = arr.getElementIndex("X")
        result = arr.evaluateParametrExpressionByIndex(idx)

        assert result == 11

    def test_returns_evaluated_integer(self):
        vp = make_vp("A", expression="4 * 2")
        arr = make_array(vp)
        idx = arr.getElementIndex("A")
        result = arr.evaluateParametrExpressionByIndex(idx)
        assert result == 8

    def test_no_string_formater_logs_warning(self, caplog):
        import logging
        arr = make_array(make_vp("A", expression="1 + 1"))
        arr.string_formater = None        # shadow class attribute on instance
        idx = arr.getElementIndex("A")
        with caplog.at_level(logging.WARNING):
            arr.evaluateParametrExpressionByIndex(idx)
        assert any("not available" in r.message for r in caplog.records)

    def test_no_string_formater_still_evaluates_with_real_utils(self):
        """
        Even without substitution, real utils.evaluateExpression should still
        resolve a self-contained numeric expression.
        """
        arr = make_array(make_vp("A", expression="3 + 3"))
        arr.string_formater = None
        idx = arr.getElementIndex("A")
        result = arr.evaluateParametrExpressionByIndex(idx)
        assert result == 6

    def test_no_utils_logs_warning(self, caplog):
        import logging
        arr = make_array(make_vp("A", expression="1"))
        arr.utils = None                  # shadow class attribute on instance
        idx = arr.getElementIndex("A")
        with caplog.at_level(logging.WARNING):
            arr.evaluateParametrExpressionByIndex(idx)
        assert any("not available" in r.message for r in caplog.records)

    def test_no_utils_returns_string_expression(self):
        """When utils is None, the substituted string expression is returned."""
        arr = make_array(make_vp("A", expression="1 + 1"))
        arr.utils = None
        idx = arr.getElementIndex("A")
        result = arr.evaluateParametrExpressionByIndex(idx)
        assert isinstance(result, str)

    def test_no_utils_leaves_parametr_value_unchanged(self):
        """When utils is None, parametr.value must NOT be mutated."""
        arr = make_array(make_vp("A", value=0, expression="1 + 1"))
        arr.utils = None
        idx = arr.getElementIndex("A")
        arr.evaluateParametrExpressionByIndex(idx)
        assert arr[arr.getElementIndex("A")].value == 0

    def test_expression_with_whitespace_is_handled(self):
        """
        Expressions with extra whitespace must still evaluate correctly.
        """
        vp = make_vp("A", expression="   2 + 3   ")
        arr = make_array(vp)

        idx = arr.getElementIndex("A")
        result = arr.evaluateParametrExpressionByIndex(idx)

        assert result == 5

    def test_expression_with_irregular_whitespace(self):
        """
        Irregular spacing between tokens must not break evaluation.
        """
        vp = make_vp("A", expression="2    +     3")
        arr = make_array(vp)

        idx = arr.getElementIndex("A")
        result = arr.evaluateParametrExpressionByIndex(idx)

        assert result == 5

    def test_number_field_does_not_affect_evaluation(self):
        """
        'number' is metadata and must not affect expression evaluation.
        """
        vp = make_vp("A", expression="2 + 3")
        vp.number = 999   # arbitrary

        arr = make_array(vp)

        idx = arr.getElementIndex("A")
        result = arr.evaluateParametrExpressionByIndex(idx)

        assert result == 5


# ===========================================================================
# 12. ValueParametrArray – container protocol
# ===========================================================================

class TestValueParametrArrayContainerProtocol:

    def test_len_empty(self):
        assert len(ValueParametrArray()) == 0

    def test_len_after_add(self):
        arr = make_array(make_vp("A"), make_vp("BB"))
        assert len(arr) == 2

    def test_iteration_yields_all_elements(self):
        arr = make_array(make_vp("A"), make_vp("BB"))
        identifiers = [e.identifier for e in arr]
        assert set(identifiers) == {"A", "BB"}

    def test_index_access_returns_correct_element(self):
        arr = make_array(make_vp("LONG"), make_vp("S"))
        assert arr[0].identifier == "LONG"

    def test_slice_returns_list(self):
        arr = make_array(make_vp("A"), make_vp("BB"), make_vp("CCC"))
        sliced = arr[0:2]
        assert len(sliced) == 2


# ===========================================================================
# 13. ValueParametrArray – __str__ / __repr__
# ===========================================================================

class TestValueParametrArrayRepresentations:

    def test_str_single_element(self):
        arr = make_array(make_vp("A", value=1))
        assert "A = 1" in str(arr)

    def test_str_multiple_elements_comma_separated(self):
        arr = make_array(make_vp("AB", value=2), make_vp("A", value=1))
        result = str(arr)
        assert "AB = 2" in result
        assert "A = 1" in result
        assert ",\n" in result

    def test_str_empty_array(self):
        assert str(ValueParametrArray()) == ""

    def test_repr_contains_class_name(self):
        assert "ValueParametrArray" in repr(ValueParametrArray())

    def test_repr_contains_element_repr(self):
        arr = make_array(make_vp("A"))
        assert "A" in repr(arr)