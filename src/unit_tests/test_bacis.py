"""
Unit tests for Basic and BasicArray.

Singleton note: Counters, StringFormater, UnsortedUnils, LoggerManager are all
singletons. Tests must not rely on counter state from prior tests. Where sequence
numbers are compared, tests work with relative values or capture the value before
and after, rather than asserting absolute numbers.
"""

import copy
import pytest
from ..classes.basic import Basic, BasicArray
from ..classes.element_types import ElementsTypes
from ..utils.counters import Counters


# ===========================================================================
# Helpers
# ===========================================================================

def make_basic(
    identifier="X",
    source_interval=(0, 0),
    element_type=ElementsTypes.NONE_ELEMENT,
) -> Basic:
    return Basic(identifier, source_interval, element_type)


def make_array(*elements: Basic, element_type=Basic) -> BasicArray:
    arr = BasicArray(element_type)
    for e in elements:
        arr.addElement(e)
    return arr


# ===========================================================================
# 1. Basic – __init__
# ===========================================================================

class TestBasicInit:

    def test_identifier_is_stored(self):
        b = make_basic(identifier="SIG")
        assert b.identifier == "SIG"

    def test_source_interval_is_stored(self):
        b = make_basic(source_interval=(3, 17))
        assert b.source_interval == (3, 17)

    def test_element_type_is_stored(self):
        b = make_basic(element_type=ElementsTypes.ACTION_ELEMENT)
        assert b.element_type is ElementsTypes.ACTION_ELEMENT

    def test_default_element_type_is_none_element(self):
        b = Basic("X")
        assert b.element_type is ElementsTypes.NONE_ELEMENT

    def test_default_source_interval_is_zero_tuple(self):
        b = Basic("X")
        assert b.source_interval == (0, 0)

    def test_number_defaults_to_none(self):
        b = make_basic()
        assert b.number is None

    def test_sequence_is_integer(self):
        b = make_basic()
        assert isinstance(b.sequence, int)

    def test_sequence_increments_between_instances(self):
        b1 = make_basic()
        b2 = make_basic()
        assert b2.sequence > b1.sequence

    def test_logger_is_assigned(self):
        b = make_basic()
        assert b.logger is not None


# ===========================================================================
# 2. Basic – getName()
# ===========================================================================

class TestBasicGetName:

    def test_returns_identifier_when_number_is_none(self):
        b = make_basic(identifier="SIG")
        assert b.getName() == "SIG"

    def test_returns_identifier_underscore_number_when_number_set(self):
        b = make_basic(identifier="SIG")
        b.number = 3
        assert b.getName() == "SIG_3"

    def test_returns_identifier_underscore_zero_when_number_is_zero(self):
        b = make_basic(identifier="SIG")
        b.number = 0
        assert b.getName() == "SIG_0"


# ===========================================================================
# 3. Basic – copy()
# ===========================================================================

class TestBasicCopy:

    def test_copy_returns_different_object(self):
        b = make_basic()
        assert b.copy() is not b

    def test_copy_preserves_identifier(self):
        b = make_basic(identifier="A")
        assert b.copy().identifier == "A"

    def test_copy_preserves_source_interval(self):
        b = make_basic(source_interval=(1, 9))
        assert b.copy().source_interval == (1, 9)

    def test_copy_preserves_element_type(self):
        b = make_basic(element_type=ElementsTypes.ACTION_ELEMENT)
        assert b.copy().element_type is ElementsTypes.ACTION_ELEMENT

    def test_copy_preserves_sequence(self):
        b = make_basic()
        assert b.copy().sequence == b.sequence

    def test_copy_preserves_number_none(self):
        b = make_basic()
        assert b.copy().number is None

    def test_copy_preserves_number_when_set(self):
        b = make_basic()
        b.number = 7
        assert b.copy().number == 7

    def test_copy_returns_basic_instance(self):
        b = make_basic()
        assert isinstance(b.copy(), Basic)

    def test_copy_identifier_mutation_does_not_affect_original(self):
        b = make_basic(identifier="A")
        copied = b.copy()
        copied.identifier = "Z"
        assert b.identifier == "A"


# ===========================================================================
# 4. Basic – __deepcopy__
# ===========================================================================

class TestBasicDeepcopy:

    def test_deepcopy_returns_different_object(self):
        b = make_basic()
        assert copy.deepcopy(b) is not b

    def test_deepcopy_preserves_identifier(self):
        b = make_basic(identifier="D")
        assert copy.deepcopy(b).identifier == "D"

    def test_deepcopy_stores_in_memo(self):
        b = make_basic()
        memo = {}
        copy.deepcopy(b, memo)
        assert id(b) in memo

    def test_deepcopy_preserves_sequence(self):
        b = make_basic()
        assert copy.deepcopy(b).sequence == b.sequence

    def test_deepcopy_preserves_number(self):
        b = make_basic()
        b.number = 5
        assert copy.deepcopy(b).number == 5


# ===========================================================================
# 5. Basic – __repr__
# ===========================================================================

class TestBasicRepr:

    def test_repr_contains_class_name(self):
        assert "Basic(" in repr(make_basic())

    def test_repr_contains_identifier(self):
        assert "'SIG'" in repr(make_basic(identifier="SIG"))

    def test_repr_contains_source_interval(self):
        assert "(2, 8)" in repr(make_basic(source_interval=(2, 8)))

    def test_repr_contains_element_type_name(self):
        b = make_basic(element_type=ElementsTypes.ACTION_ELEMENT)
        assert "ACTION_ELEMENT" in repr(b)

    def test_repr_contains_number(self):
        b = make_basic()
        b.number = 4
        assert "4" in repr(b)


# ===========================================================================
# 6. Basic – class-level utilities accessible on instance
# ===========================================================================

class TestBasicClassLevelUtilities:

    def test_counters_is_singleton(self):
        b1 = make_basic()
        b2 = make_basic()
        assert b1.counters is b2.counters

    def test_string_formater_is_singleton(self):
        b1 = make_basic()
        b2 = make_basic()
        assert b1.string_formater is b2.string_formater

    def test_utils_is_singleton(self):
        b1 = make_basic()
        b2 = make_basic()
        assert b1.utils is b2.utils


# ===========================================================================
# 7. BasicArray – __init__
# ===========================================================================

class TestBasicArrayInit:

    def test_starts_empty(self):
        assert len(BasicArray()) == 0

    def test_default_element_type_is_basic(self):
        assert BasicArray().element_type is Basic

    def test_custom_element_type_is_stored(self):
        arr = BasicArray(element_type=Basic)
        assert arr.element_type is Basic

    def test_logger_is_assigned(self):
        assert BasicArray().logger is not None

    def test_elements_list_starts_empty(self):
        assert BasicArray().elements == []


# ===========================================================================
# 8. BasicArray – addElement()
# ===========================================================================

class TestBasicArrayAddElement:

    def test_element_is_present_after_add(self):
        arr = BasicArray()
        b = make_basic("A")
        arr.addElement(b)
        assert any(e.identifier == "A" for e in arr)

    def test_length_increases_after_add(self):
        arr = BasicArray()
        arr.addElement(make_basic())
        assert len(arr) == 1

    def test_returns_index_zero_for_first_element(self):
        arr = BasicArray()
        idx = arr.addElement(make_basic())
        assert idx == 0

    def test_returns_correct_index_for_second_element(self):
        arr = BasicArray()
        arr.addElement(make_basic("A"))
        idx = arr.addElement(make_basic("B"))
        assert idx == 1

    def test_wrong_type_logs_warning_not_raises(self, caplog):
        import logging
        arr = BasicArray()
        with caplog.at_level(logging.WARNING):
            arr.addElement("not_a_basic")
        assert any("not_a_basic" in r.message or "str" in r.message
                   for r in caplog.records)

    def test_wrong_type_element_still_appended(self):
        arr = BasicArray()
        arr.addElement("not_a_basic")
        assert len(arr) == 1


# ===========================================================================
# 9. BasicArray – __len__, __iter__, __getitem__
# ===========================================================================

class TestBasicArrayContainerProtocol:

    def test_len_empty(self):
        assert len(BasicArray()) == 0

    def test_len_after_adds(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        assert len(arr) == 2

    def test_iteration_yields_all_elements(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        identifiers = {e.identifier for e in arr}
        assert identifiers == {"A", "B"}

    def test_index_access_returns_correct_element(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        assert arr[0].identifier == "A"

    def test_slice_returns_list(self):
        arr = make_array(make_basic("A"), make_basic("B"), make_basic("C"))
        assert len(arr[0:2]) == 2


# ===========================================================================
# 10. BasicArray – copy() and __deepcopy__
# ===========================================================================

class TestBasicArrayCopy:

    def test_copy_returns_different_array(self):
        arr = make_array(make_basic("A"))
        assert arr.copy() is not arr

    def test_copy_element_is_different_object(self):
        b = make_basic("A")
        arr = make_array(b)
        assert arr.copy()[0] is not b

    def test_copy_preserves_element_count(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        assert len(arr.copy()) == 2

    def test_copy_mutation_does_not_affect_original(self):
        arr = make_array(make_basic("A"))
        copied = arr.copy()
        copied[0].identifier = "Z"
        assert arr[0].identifier == "A"

    def test_copy_of_empty_array_is_empty(self):
        assert len(BasicArray().copy()) == 0

    def test_deepcopy_returns_different_array(self):
        arr = make_array(make_basic("A"))
        assert copy.deepcopy(arr) is not arr

    def test_deepcopy_element_is_different_object(self):
        b = make_basic("A")
        arr = make_array(b)
        assert copy.deepcopy(arr)[0] is not b

    def test_deepcopy_stores_in_memo(self):
        arr = make_array(make_basic("A"))
        memo = {}
        copy.deepcopy(arr, memo)
        assert id(arr) in memo

    def test_deepcopy_preserves_element_count(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        assert len(copy.deepcopy(arr)) == 2


# ===========================================================================
# 11. BasicArray – reverse() and reverse_copy()
# ===========================================================================

class TestBasicArrayReverse:

    def test_reverse_modifies_in_place(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        arr.reverse()
        assert arr[0].identifier == "B"

    def test_reverse_returns_same_array_object(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        result = arr.reverse()
        assert result is arr

    def test_reverse_copy_returns_different_array(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        assert arr.reverse_copy() is not arr

    def test_reverse_copy_does_not_modify_original(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        arr.reverse_copy()
        assert arr[0].identifier == "A"

    def test_reverse_copy_order_is_reversed(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        reversed_arr = arr.reverse_copy()
        assert reversed_arr[0].identifier == "B"


# ===========================================================================
# 12. BasicArray – insert()
# ===========================================================================

class TestBasicArrayInsert:

    def test_insert_at_index_zero(self):
        arr = make_array(make_basic("B"))
        arr.insert(0, make_basic("A"))
        assert arr[0].identifier == "A"

    def test_insert_increases_length(self):
        arr = make_array(make_basic("B"))
        arr.insert(0, make_basic("A"))
        assert len(arr) == 2

    def test_insert_at_end(self):
        arr = make_array(make_basic("A"))
        arr.insert(1, make_basic("B"))
        assert arr[1].identifier == "B"


# ===========================================================================
# 13. BasicArray – getElementsIE()
# ===========================================================================

class TestBasicArrayGetElementsIE:

    @pytest.fixture
    def two_element_array(self) -> BasicArray:
        b1 = make_basic("A", element_type=ElementsTypes.ACTION_ELEMENT)
        b2 = make_basic("B", element_type=ElementsTypes.CONDITION_ELEMENT)
        return make_array(b1, b2)

    # --- no filters ---

    def test_no_filters_returns_basic_array(self, two_element_array):
        assert isinstance(two_element_array.getElementsIE(), BasicArray)

    def test_no_filters_returns_all_elements(self, two_element_array):
        assert len(two_element_array.getElementsIE()) == 2

    def test_no_filters_returns_new_object(self, two_element_array):
        assert two_element_array.getElementsIE() is not two_element_array

    # --- include ---

    def test_include_returns_only_matching_type(self, two_element_array):
        res = two_element_array.getElementsIE(include=ElementsTypes.ACTION_ELEMENT)
        assert all(e.element_type is ElementsTypes.ACTION_ELEMENT for e in res)

    def test_include_result_length(self, two_element_array):
        res = two_element_array.getElementsIE(include=ElementsTypes.ACTION_ELEMENT)
        assert len(res) == 1

    def test_include_excludes_non_matching(self, two_element_array):
        res = two_element_array.getElementsIE(include=ElementsTypes.ACTION_ELEMENT)
        assert not any(e.identifier == "B" for e in res)

    # --- exclude ---

    def test_exclude_removes_matching_type(self, two_element_array):
        res = two_element_array.getElementsIE(exclude=ElementsTypes.ACTION_ELEMENT)
        assert not any(e.identifier == "A" for e in res)

    def test_exclude_keeps_non_matching(self, two_element_array):
        res = two_element_array.getElementsIE(exclude=ElementsTypes.ACTION_ELEMENT)
        assert any(e.identifier == "B" for e in res)

    # --- include_identifier ---

    def test_include_identifier_returns_only_matching(self, two_element_array):
        res = two_element_array.getElementsIE(include_identifier="A")
        assert len(res) == 1

    def test_include_identifier_correct_element(self, two_element_array):
        res = two_element_array.getElementsIE(include_identifier="A")
        assert res[0].identifier == "A"

    # --- exclude_identifier ---

    def test_exclude_identifier_removes_matching(self, two_element_array):
        res = two_element_array.getElementsIE(exclude_identifier="A")
        assert not any(e.identifier == "A" for e in res)

    def test_exclude_identifier_keeps_other(self, two_element_array):
        res = two_element_array.getElementsIE(exclude_identifier="A")
        assert any(e.identifier == "B" for e in res)

    # --- combined ---

    def test_combined_include_and_exclude_identifier_empty(self, two_element_array):
        """include ACTION_ELEMENT but exclude 'A' → empty."""
        res = two_element_array.getElementsIE(
            include=ElementsTypes.ACTION_ELEMENT,
            exclude_identifier="A",
        )
        assert len(res) == 0

    # --- empty array ---

    def test_filter_on_empty_array_returns_empty(self):
        res = BasicArray().getElementsIE(include=ElementsTypes.ACTION_ELEMENT)
        assert len(res) == 0

    # --- filtered path returns same objects ---

    def test_filter_returns_same_objects_not_copies(self, two_element_array):
        res = two_element_array.getElementsIE(include_identifier="A")
        original = next(e for e in two_element_array if e.identifier == "A")
        assert res[0] is original

    def test_no_filters_mutation_does_not_affect_original(self, two_element_array):
        """No-filter path returns clones — mutating result leaves original intact."""
        res = two_element_array.getElementsIE()
        res[0].identifier = "MUTATED"
        assert two_element_array[0].identifier != "MUTATED"


class TestBasicArrayKnownBugs:
    BUG_FILTER_RETURNS_REFERENCES = (
        "BUG: getElementsIE() with filters appends original element references, "
        "not copies. Mutating the result silently mutates the source array. "
        "Inconsistent with no-filter path which returns clones via self.copy()."
    )

    @pytest.mark.xfail(strict=True, reason=BUG_FILTER_RETURNS_REFERENCES)
    def test_filtered_result_mutation_does_not_affect_original(self):
        b1 = make_basic("A", element_type=ElementsTypes.ACTION_ELEMENT)
        b2 = make_basic("B", element_type=ElementsTypes.CONDITION_ELEMENT)
        arr = make_array(b1, b2)
        res = arr.getElementsIE(include_identifier="A")
        res[0].identifier = "MUTATED"
        assert arr[0].identifier != "MUTATED"

# ===========================================================================
# 14. BasicArray – __iadd__
# ===========================================================================

class TestBasicArrayIadd:

    def test_iadd_basic_array_extends_elements(self):
        arr1 = make_array(make_basic("A"))
        arr2 = make_array(make_basic("B"))
        arr1 += arr2
        assert len(arr1) == 2

    def test_iadd_basic_array_preserves_elements(self):
        arr1 = make_array(make_basic("A"))
        arr2 = make_array(make_basic("B"))
        arr1 += arr2
        assert any(e.identifier == "B" for e in arr1)

    def test_iadd_basic_element_adds_it(self):
        arr = make_array(make_basic("A"))
        arr += make_basic("B")
        assert len(arr) == 2

    def test_iadd_basic_element_preserves_original(self):
        arr = make_array(make_basic("A"))
        arr += make_basic("B")
        assert any(e.identifier == "A" for e in arr)

    def test_iadd_raises_type_error_for_invalid_type(self):
        arr = BasicArray()
        with pytest.raises(TypeError):
            arr += 42

    def test_iadd_type_mismatch_logs_warning(self, caplog):
        import logging
        from ..classes.value_parametrs import ValueParametr
        arr1 = BasicArray(element_type=Basic)
        arr2 = BasicArray(element_type=ValueParametr)
        arr2.elements.append(ValueParametr("V", (0, 0)))
        with caplog.at_level(logging.WARNING):
            arr1 += arr2
        assert any("mismatch" in r.message.lower() or "type" in r.message.lower()
                   for r in caplog.records)

    def test_iadd_returns_self(self):
        arr = make_array(make_basic("A"))
        original_id = id(arr)
        arr += make_basic("B")
        assert id(arr) == original_id


# ===========================================================================
# 15. BasicArray – getElement() and getElementIndex()
# ===========================================================================

class TestBasicArrayGetElement:

    def test_get_element_returns_matching(self):
        b = make_basic("TARGET")
        arr = make_array(make_basic("A"), b)
        assert arr.getElement("TARGET") is b

    def test_get_element_returns_none_when_not_found(self):
        arr = make_array(make_basic("A"))
        assert arr.getElement("MISSING") is None

    def test_get_element_returns_none_for_empty_array(self):
        assert BasicArray().getElement("X") is None

    def test_get_element_index_returns_correct_index(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        assert arr.getElementIndex("B") == 1

    def test_get_element_index_returns_none_when_not_found(self):
        arr = make_array(make_basic("A"))
        assert arr.getElementIndex("MISSING") is None

    def test_get_element_index_returns_none_for_empty_array(self):
        assert BasicArray().getElementIndex("X") is None


# ===========================================================================
# 16. BasicArray – getElementByIndex() and getLastElement()
# ===========================================================================

class TestBasicArrayIndexAccess:

    def test_get_element_by_index_returns_correct_element(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        assert arr.getElementByIndex(1).identifier == "B"

    def test_get_element_by_index_raises_for_out_of_bounds(self):
        arr = make_array(make_basic("A"))
        with pytest.raises(IndexError):
            arr.getElementByIndex(99)

    def test_get_element_by_index_raises_for_empty_array(self):
        with pytest.raises(IndexError):
            BasicArray().getElementByIndex(0)

    def test_get_last_element_returns_last(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        assert arr.getLastElement().identifier == "B"

    def test_get_last_element_returns_none_for_empty(self):
        assert BasicArray().getLastElement() is None


# ===========================================================================
# 17. BasicArray – removeElement() and removeElementByIndex()
# ===========================================================================

class TestBasicArrayRemove:

    def test_remove_element_decreases_length(self):
        b = make_basic("A")
        arr = make_array(b)
        arr.removeElement(b)
        assert len(arr) == 0

    def test_remove_element_removes_correct_element(self):
        b = make_basic("A")
        arr = make_array(make_basic("B"), b)
        arr.removeElement(b)
        assert not any(e.identifier == "A" for e in arr)

    def test_remove_element_by_index_decreases_length(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        arr.removeElementByIndex(0)
        assert len(arr) == 1

    def test_remove_element_by_index_removes_correct_element(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        arr.removeElementByIndex(0)
        assert arr[0].identifier == "B"

    def test_remove_element_by_index_out_of_bounds_does_nothing(self):
        arr = make_array(make_basic("A"))
        arr.removeElementByIndex(99)
        assert len(arr) == 1

    def test_remove_element_by_index_negative_does_nothing(self):
        arr = make_array(make_basic("A"))
        arr.removeElementByIndex(-1)
        assert len(arr) == 1


# ===========================================================================
# 18. BasicArray – getElements()
# ===========================================================================

class TestBasicArrayGetElements:

    def test_get_elements_returns_list(self):
        arr = make_array(make_basic("A"))
        assert isinstance(arr.getElements(), list)

    def test_get_elements_returns_all(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        assert len(arr.getElements()) == 2

    def test_get_elements_returns_same_list_reference(self):
        arr = make_array(make_basic("A"))
        assert arr.getElements() is arr.elements


# ===========================================================================
# 19. BasicArray – checkSourceInteval()
# ===========================================================================

class TestBasicArrayCheckSourceInterval:

    def test_returns_false_when_interval_contained(self):
        b = make_basic(source_interval=(0, 100))
        arr = make_array(b)
        assert arr.checkSourceInteval((10, 50)) is False

    def test_returns_true_when_interval_not_contained(self):
        b = make_basic(source_interval=(0, 10))
        arr = make_array(b)
        assert arr.checkSourceInteval((20, 50)) is True

    def test_returns_true_for_empty_array(self):
        assert BasicArray().checkSourceInteval((0, 10)) is True


# ===========================================================================
# 20. BasicArray – __repr__
# ===========================================================================

class TestBasicArrayRepr:

    def test_repr_contains_class_name(self):
        assert "BasicArray(" in repr(BasicArray())

    def test_repr_contains_element_type_name(self):
        assert "Basic" in repr(BasicArray())

    def test_repr_contains_element_count(self):
        arr = make_array(make_basic("A"), make_basic("B"))
        assert "2" in repr(arr)

    def test_repr_contains_element_identifier(self):
        arr = make_array(make_basic("MYSIG"))
        assert "MYSIG" in repr(arr)


# ===========================================================================
# 21. BasicArray – class-level utilities accessible on instance
# ===========================================================================

class TestBasicArrayClassLevelUtilities:

    def test_counters_is_singleton(self):
        arr1 = BasicArray()
        arr2 = BasicArray()
        assert arr1.counters is arr2.counters

    def test_string_formater_is_singleton(self):
        arr1 = BasicArray()
        arr2 = BasicArray()
        assert arr1.string_formater is arr2.string_formater

    def test_utils_is_singleton(self):
        arr1 = BasicArray()
        arr2 = BasicArray()
        assert arr1.utils is arr2.utils

    def test_basic_and_basic_array_share_counters(self):
        b = make_basic()
        arr = BasicArray()
        assert b.counters is arr.counters