"""
Unit tests for Typedef and TypedefArray.

Dependencies (Basic, BasicArray, Declaration, DeclarationArray, DeclTypes,
ElementsTypes) are exercised through their real implementations.
"""

from unittest import result

import pytest
import logging
from ..classes.typedef import Typedef, TypedefArray
from ..classes.declarations import Declaration, DeclarationArray, DeclTypes, AplanDeclType
from ..classes.element_types import ElementsTypes
from ..classes.basic import Basic, BasicArray


# ===========================================================================
# Helpers
# ===========================================================================

def make_typedef(
    identifier="MyType",
    unique_identifier="module_MyType",
    source_interval=(0, 10),
    file_path="/src/file.sv",
    data_type=DeclTypes.ENUM_TYPE,
    element_type=ElementsTypes.NONE_ELEMENT,
) -> Typedef:
    return Typedef(
        identifier,
        unique_identifier,
        source_interval,
        file_path,
        data_type,
        element_type,
    )


def make_declaration(
    identifier="field",
    data_type=DeclTypes.INT,
    source_interval=(0, 5),
    name_space_level=0,
) -> Declaration:
    return Declaration(
        data_type=data_type,
        identifier=identifier,
        source_interval=source_interval,
        name_space_level=name_space_level,
    )


def make_array(*typedefs: Typedef) -> TypedefArray:
    arr = TypedefArray()
    for t in typedefs:
        arr.addElement(t)
    return arr


# ===========================================================================
# 1. Typedef – __init__
# ===========================================================================

class TestTypedefInit:

    def test_identifier_is_stored(self):
        td = make_typedef(identifier="State")
        assert td.identifier == "State"

    def test_unique_identifier_is_stored(self):
        td = make_typedef(unique_identifier="mod_State")
        assert td.unique_identifier == "mod_State"

    def test_source_interval_is_stored(self):
        td = make_typedef(source_interval=(5, 20))
        assert td.source_interval == (5, 20)

    def test_file_path_is_stored(self):
        td = make_typedef(file_path="/hdl/top.sv")
        assert td.file_path == "/hdl/top.sv"

    def test_data_type_is_stored(self):
        td = make_typedef(data_type=DeclTypes.STRUCT_TYPE)
        assert td.data_type is DeclTypes.STRUCT_TYPE

    def test_element_type_default_is_none_element(self):
        td = make_typedef()
        assert td.element_type is ElementsTypes.NONE_ELEMENT

    def test_element_type_custom_is_stored(self):
        td = make_typedef(element_type=ElementsTypes.MODULE_ELEMENT)
        assert td.element_type is ElementsTypes.MODULE_ELEMENT

    def test_declarations_starts_empty(self):
        td = make_typedef()
        assert len(td.declarations) == 0

    def test_declarations_is_declaration_array(self):
        td = make_typedef()
        assert isinstance(td.declarations, DeclarationArray)

    def test_inherits_from_basic(self):
        td = make_typedef()
        assert isinstance(td, Basic)


# ===========================================================================
# 2. Typedef – checkDecl()
# ===========================================================================

class TestTypedefCheckDecl:

    def test_returns_true_when_declaration_exists(self):
        td = make_typedef()
        td.declarations.addElement(make_declaration("WIDTH"))
        assert td.checkDecl("WIDTH") is True

    def test_returns_false_when_declaration_missing(self):
        td = make_typedef()
        assert td.checkDecl("MISSING") is False

    def test_returns_false_on_empty_declarations(self):
        td = make_typedef()
        assert td.checkDecl("ANY") is False


# ===========================================================================
# 3. Typedef – copy()
# ===========================================================================

class TestTypedefCopy:

    def test_copy_returns_different_object(self):
        td = make_typedef()
        assert td.copy() is not td

    def test_copy_preserves_identifier(self):
        td = make_typedef(identifier="T")
        assert td.copy().identifier == "T"

    def test_copy_preserves_unique_identifier(self):
        td = make_typedef(unique_identifier="mod_T")
        assert td.copy().unique_identifier == "mod_T"

    def test_copy_preserves_source_interval(self):
        td = make_typedef(source_interval=(1, 9))
        assert td.copy().source_interval == (1, 9)

    def test_copy_preserves_file_path(self):
        td = make_typedef(file_path="/a/b.sv")
        assert td.copy().file_path == "/a/b.sv"

    def test_copy_preserves_data_type(self):
        td = make_typedef(data_type=DeclTypes.STRUCT_TYPE)
        assert td.copy().data_type is DeclTypes.STRUCT_TYPE

    def test_copy_preserves_element_type(self):
        td = make_typedef(element_type=ElementsTypes.MODULE_ELEMENT)
        assert td.copy().element_type is ElementsTypes.MODULE_ELEMENT

    def test_copy_declarations_are_independent(self):
        td = make_typedef()
        td.declarations.addElement(make_declaration("FIELD"))
        copied = td.copy()
        copied.declarations.addElement(make_declaration("EXTRA"))
        assert len(td.declarations) == 1

    def test_copy_returns_typedef_instance(self):
        td = make_typedef()
        assert isinstance(td.copy(), Typedef)

    def test_copy_declarations_element_is_different_object(self):
        td = make_typedef()
        td.declarations.addElement(make_declaration("FIELD"))
        copied = td.copy()
        assert copied.declarations.getElement("FIELD") is not \
               td.declarations.getElement("FIELD")


# ===========================================================================
# 4. Typedef – replaceTokensWithExpressions()
# ===========================================================================

class TestTypedefReplaceTokensWithExpressions:

    def _make_typed_enum_member(self, identifier: str, expression: str, source_interval=(0, 0)) -> Declaration:
        decl = Declaration(
            data_type=DeclTypes.ENUM_TYPE,
            identifier=identifier,
            expression=expression,
            source_interval=source_interval,
        )
        return decl

    def test_known_token_is_replaced_with_expression(self):
        td = make_typedef(data_type=DeclTypes.ENUM_TYPE)
        td.declarations.addElement(
            self._make_typed_enum_member("RED", "0")
        )
        result = td.replaceTokensWithExpressions(["RED"])
        assert result == ["0"]

    def test_unknown_token_is_kept_unchanged(self):
        td = make_typedef(data_type=DeclTypes.ENUM_TYPE)
        result = td.replaceTokensWithExpressions(["UNKNOWN"])
        assert result == ["UNKNOWN"]

    def test_mixed_tokens_replaced_and_kept(self):
        td = make_typedef(data_type=DeclTypes.ENUM_TYPE)
        td.declarations.addElement(
            self._make_typed_enum_member("GREEN", "1")
        )
        result = td.replaceTokensWithExpressions(["GREEN", "UNKNOWN"])
        assert result == ["1", "UNKNOWN"]

    def test_empty_token_list_returns_empty(self):
        td = make_typedef()
        result = td.replaceTokensWithExpressions([])
        assert result == []

    def test_returns_list(self):
        td = make_typedef()
        result = td.replaceTokensWithExpressions(["X"])
        assert isinstance(result, list)

    def test_multiple_known_tokens_all_replaced(self):
        td = make_typedef(data_type=DeclTypes.ENUM_TYPE)
        td.declarations.addElement(self._make_typed_enum_member("A", "10", (0, 1)))
        td.declarations.addElement(self._make_typed_enum_member("B", "20", (2, 3)))
        result = td.replaceTokensWithExpressions(["A", "B"])
        assert result == ["10", "20"]


# ===========================================================================
# 5. Typedef – __str__
# ===========================================================================

class TestTypedefStr:

    def test_str_enum_type_contains_unique_identifier(self):
        td = make_typedef(unique_identifier="mod_State", data_type=DeclTypes.ENUM_TYPE)
        assert "mod_State" in str(td)

    def test_str_enum_type_contains_member_names(self):
        td = make_typedef(data_type=DeclTypes.ENUM_TYPE)
        decl = make_declaration("IDLE")
        decl.number = None
        td.declarations.addElement(decl)
        result = str(td)
        assert "IDLE" in result

    def test_str_struct_type_contains_obj_keyword(self):
        td = make_typedef(data_type=DeclTypes.STRUCT_TYPE)
        assert "obj" in str(td)

    def test_str_union_type_contains_obj_keyword(self):
        td = make_typedef(data_type=DeclTypes.UNION_TYPE)
        assert "obj" in str(td)

    def test_str_other_type_contains_data_type_name(self):
        td = make_typedef(data_type=DeclTypes.NONE)
        result = str(td)
        assert "NONE" in result

    def test_str_other_type_with_declarations_contains_decl(self):
        td = make_typedef(data_type=DeclTypes.NONE)
        td.declarations.addElement(make_declaration("field_x"))
        result = str(td)
        assert "field_x" in result

    def test_str_enum_type_uses_parentheses(self):
        td = make_typedef(data_type=DeclTypes.ENUM_TYPE)
        result = str(td)
        assert "(" in result and ")" in result

    def test_str_struct_type_uses_parentheses(self):
        td = make_typedef(data_type=DeclTypes.STRUCT_TYPE)
        result = str(td)
        assert "(" in result
        assert ")" in result
        assert result.startswith("module_MyType: obj (")


# ===========================================================================
# 6. Typedef – __repr__
# ===========================================================================

class TestTypedefRepr:

    def test_repr_contains_class_name(self):
        assert "Typedef(" in repr(make_typedef())

    def test_repr_contains_identifier(self):
        assert "'MyType'" in repr(make_typedef(identifier="MyType"))

    def test_repr_contains_unique_identifier(self):
        assert "'mod_MyType'" in repr(make_typedef(unique_identifier="mod_MyType"))

    def test_repr_contains_file_path(self):
        assert "'/src/file.sv'" in repr(make_typedef(file_path="/src/file.sv"))

    def test_repr_contains_data_type(self):
        result = repr(make_typedef(data_type=DeclTypes.ENUM_TYPE))
        assert "ENUM_TYPE" in result


# ===========================================================================
# 7. TypedefArray – __init__
# ===========================================================================

class TestTypedefArrayInit:

    def test_element_type_is_typedef(self):
        assert TypedefArray().element_type is Typedef

    def test_starts_empty(self):
        assert len(TypedefArray()) == 0

    def test_inherits_from_basic_array(self):
        assert isinstance(TypedefArray(), BasicArray)


# ===========================================================================
# 8. TypedefArray – addElement()
# ===========================================================================

class TestTypedefArrayAddElement:

    def test_raises_type_error_for_wrong_type(self):
        arr = TypedefArray()
        with pytest.raises(TypeError):
            arr.addElement("not_a_typedef")

    def test_type_error_message_mentions_typedef(self):
        arr = TypedefArray()
        with pytest.raises(TypeError, match="Typedef"):
            arr.addElement(42)

    def test_element_is_present_after_add(self):
        arr = TypedefArray()
        td = make_typedef(identifier="T")
        arr.addElement(td)
        assert any(e.identifier == "T" for e in arr)

    def test_length_increases_after_add(self):
        arr = TypedefArray()
        arr.addElement(make_typedef())
        assert len(arr) == 1

    def test_returns_true_on_first_add(self):
        arr = TypedefArray()
        success, _ = arr.addElement(make_typedef())
        assert success is True

    def test_returns_index_on_first_add(self):
        arr = TypedefArray()
        _, idx = arr.addElement(make_typedef(identifier="T"))
        assert arr[idx].identifier == "T"

    def test_duplicate_by_identifier_not_added(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="T", unique_identifier="u1", source_interval=(0, 5)))
        success, _ = arr.addElement(
            make_typedef(identifier="T", unique_identifier="u2", source_interval=(10, 15))
        )
        assert success is False

    def test_duplicate_by_unique_identifier_not_added(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="A", unique_identifier="shared_uid", source_interval=(0, 5)))
        success, _ = arr.addElement(
            make_typedef(identifier="B", unique_identifier="shared_uid", source_interval=(10, 15))
        )
        assert success is False

    def test_duplicate_by_source_interval_not_added(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="A", unique_identifier="u1", source_interval=(0, 5)))
        success, _ = arr.addElement(
            make_typedef(identifier="B", unique_identifier="u2", source_interval=(0, 5))
        )
        assert success is False

    def test_duplicate_returns_existing_element_index(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="T", unique_identifier="u1", source_interval=(0, 5)))
        _, idx = arr.addElement(
            make_typedef(identifier="T", unique_identifier="u2", source_interval=(10, 15))
        )
        assert arr[idx].identifier == "T"

    def test_duplicate_does_not_increase_length(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="T", unique_identifier="u1", source_interval=(0, 5)))
        arr.addElement(make_typedef(identifier="T", unique_identifier="u2", source_interval=(10, 15)))
        assert len(arr) == 1

    def test_unique_elements_all_added(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="A", unique_identifier="u1", source_interval=(0, 5)))
        arr.addElement(make_typedef(identifier="B", unique_identifier="u2", source_interval=(6, 10)))
        assert len(arr) == 2


# ===========================================================================
# 9. TypedefArray – copy()
# ===========================================================================

class TestTypedefArrayCopy:

    def test_copy_returns_different_array_object(self):
        arr = make_array(make_typedef())
        assert arr.copy() is not arr

    def test_copy_contains_same_number_of_elements(self):
        arr = make_array(
            make_typedef(identifier="A", unique_identifier="u1", source_interval=(0, 5)),
            make_typedef(identifier="B", unique_identifier="u2", source_interval=(6, 10)),
        )
        assert len(arr.copy()) == 2

    def test_copy_element_is_different_object(self):
        td = make_typedef()
        arr = make_array(td)
        assert arr.copy()[0] is not td

    def test_copy_mutation_does_not_affect_original(self):
        arr = make_array(make_typedef(file_path="/original.sv"))
        copied = arr.copy()
        copied[0].file_path = "/mutated.sv"
        assert arr[0].file_path == "/original.sv"

    def test_copy_returns_typedef_array_instance(self):
        arr = make_array(make_typedef())
        assert isinstance(arr.copy(), TypedefArray)

    def test_copy_of_empty_array_is_empty(self):
        assert len(TypedefArray().copy()) == 0


# ===========================================================================
# 10. TypedefArray – getLastElement()
# ===========================================================================

class TestTypedefArrayGetLastElement:

    def test_returns_none_for_empty_array(self):
        assert TypedefArray().getLastElement() is None

    def test_returns_last_added_element(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="A", unique_identifier="u1", source_interval=(0, 5)))
        td_b = make_typedef(identifier="B", unique_identifier="u2", source_interval=(6, 10))
        arr.addElement(td_b)
        assert arr.getLastElement().identifier == "B"

    def test_returns_typedef_instance(self):
        arr = make_array(make_typedef())
        assert isinstance(arr.getLastElement(), Typedef)


# ===========================================================================
# 11. TypedefArray – getElementByIndex()
# ===========================================================================

class TestTypedefArrayGetElementByIndex:

    def test_retrieves_element_at_index_zero(self):
        arr = make_array(make_typedef(identifier="T"))
        assert arr.getElementByIndex(0).identifier == "T"

    def test_raises_index_error_for_empty_array(self):
        with pytest.raises(IndexError):
            TypedefArray().getElementByIndex(0)

    def test_raises_index_error_for_out_of_bounds(self):
        arr = make_array(make_typedef())
        with pytest.raises(IndexError):
            arr.getElementByIndex(99)

    def test_returns_typedef_instance(self):
        arr = make_array(make_typedef())
        assert isinstance(arr.getElementByIndex(0), Typedef)


# ===========================================================================
# 12. TypedefArray – findElementWithSource()
# ===========================================================================

class TestTypedefArrayFindElementWithSource:

    def test_finds_by_identifier(self):
        td = make_typedef(identifier="T", unique_identifier="u1", source_interval=(0, 5))
        arr = make_array(td)
        result = arr.findElementWithSource("T", "no_match", (99, 99))
        assert result is td

    def test_finds_by_unique_identifier(self):
        td = make_typedef(identifier="T", unique_identifier="u_special", source_interval=(0, 5))
        arr = make_array(td)
        result = arr.findElementWithSource("no_match", "u_special", (99, 99))
        assert result is td

    def test_finds_by_source_interval(self):
        td = make_typedef(identifier="T", unique_identifier="u1", source_interval=(7, 14))
        arr = make_array(td)
        result = arr.findElementWithSource("no_match", "no_match", (7, 14))
        assert result is td

    def test_returns_none_when_no_match(self):
        arr = make_array(
            make_typedef(identifier="T", unique_identifier="u1", source_interval=(0, 5))
        )
        result = arr.findElementWithSource("X", "Y", (99, 99))
        assert result is None

    def test_returns_none_for_empty_array(self):
        result = TypedefArray().findElementWithSource("T", "u1", (0, 5))
        assert result is None

    def test_returns_first_match(self):
        td_a = make_typedef(identifier="SAME", unique_identifier="u1", source_interval=(0, 5))
        td_b = make_typedef(identifier="B", unique_identifier="u2", source_interval=(6, 10))
        arr = TypedefArray()
        arr.addElement(td_a)
        arr.addElement(td_b)
        result = arr.findElementWithSource("SAME", "no_match", (99, 99))
        assert result is td_a


# ===========================================================================
# 13. TypedefArray – getElementsIE()
# ===========================================================================

class TestTypedefArrayGetElementsIE:

    @pytest.fixture
    def populated_array(self) -> TypedefArray:
        td1 = make_typedef(
            identifier="EnumType",
            unique_identifier="u1",
            source_interval=(0, 5),
            file_path="/a.sv",
            data_type=DeclTypes.ENUM_TYPE,
            element_type=ElementsTypes.MODULE_ELEMENT,
        )
        td2 = make_typedef(
            identifier="StructType",
            unique_identifier="u2",
            source_interval=(6, 10),
            file_path="/b.sv",
            data_type=DeclTypes.STRUCT_TYPE,
            element_type=ElementsTypes.PACKAGE_ELEMENT,
        )
        arr = TypedefArray()
        arr.addElement(td1)
        arr.addElement(td2)
        return arr

    # --- no filters ---

    def test_no_filters_returns_typedef_array(self, populated_array):
        assert isinstance(populated_array.getElementsIE(), TypedefArray)

    def test_no_filters_returns_all_elements(self, populated_array):
        assert len(populated_array.getElementsIE()) == 2

    def test_no_filters_returns_new_object(self, populated_array):
        assert populated_array.getElementsIE() is not populated_array

    def test_no_filters_returns_copies_not_same_objects(self, populated_array):
        res = populated_array.getElementsIE()
        assert res[0] is not populated_array[0]

    # --- include_type ---

    def test_include_type_returns_matching(self, populated_array):
        res = populated_array.getElementsIE(include_type=ElementsTypes.MODULE_ELEMENT)
        assert any(e.identifier == "EnumType" for e in res)

    def test_include_type_excludes_non_matching(self, populated_array):
        res = populated_array.getElementsIE(include_type=ElementsTypes.MODULE_ELEMENT)
        assert not any(e.identifier == "StructType" for e in res)

    # --- exclude_type ---

    def test_exclude_type_removes_matching(self, populated_array):
        res = populated_array.getElementsIE(exclude_type=ElementsTypes.MODULE_ELEMENT)
        assert not any(e.identifier == "EnumType" for e in res)

    def test_exclude_type_keeps_non_matching(self, populated_array):
        res = populated_array.getElementsIE(exclude_type=ElementsTypes.MODULE_ELEMENT)
        assert any(e.identifier == "StructType" for e in res)

    # --- include_identifier ---

    def test_include_identifier_returns_only_matching(self, populated_array):
        res = populated_array.getElementsIE(include_identifier="EnumType")
        assert len(res) == 1

    def test_include_identifier_correct_element(self, populated_array):
        res = populated_array.getElementsIE(include_identifier="EnumType")
        assert res[0].identifier == "EnumType"

    # --- exclude_identifier ---

    def test_exclude_identifier_removes_matching(self, populated_array):
        res = populated_array.getElementsIE(exclude_identifier="EnumType")
        assert not any(e.identifier == "EnumType" for e in res)

    def test_exclude_identifier_keeps_other(self, populated_array):
        res = populated_array.getElementsIE(exclude_identifier="EnumType")
        assert any(e.identifier == "StructType" for e in res)

    # --- file_path ---

    def test_file_path_returns_only_matching(self, populated_array):
        res = populated_array.getElementsIE(file_path="/a.sv")
        assert len(res) == 1

    def test_file_path_correct_element(self, populated_array):
        res = populated_array.getElementsIE(file_path="/a.sv")
        assert res[0].identifier == "EnumType"

    def test_file_path_no_match_returns_empty(self, populated_array):
        res = populated_array.getElementsIE(file_path="/nonexistent.sv")
        assert len(res) == 0

    # --- include_data_type ---

    def test_include_data_type_returns_matching(self, populated_array):
        res = populated_array.getElementsIE(include_data_type=DeclTypes.ENUM_TYPE)
        assert any(e.identifier == "EnumType" for e in res)

    def test_include_data_type_excludes_non_matching(self, populated_array):
        res = populated_array.getElementsIE(include_data_type=DeclTypes.ENUM_TYPE)
        assert not any(e.identifier == "StructType" for e in res)

    # --- exclude_data_type ---

    def test_exclude_data_type_removes_matching(self, populated_array):
        res = populated_array.getElementsIE(exclude_data_type=DeclTypes.ENUM_TYPE)
        assert not any(e.identifier == "EnumType" for e in res)

    def test_exclude_data_type_keeps_non_matching(self, populated_array):
        res = populated_array.getElementsIE(exclude_data_type=DeclTypes.ENUM_TYPE)
        assert any(e.identifier == "StructType" for e in res)

    # --- combined filters ---

    def test_combined_include_data_type_and_exclude_identifier_empty(self, populated_array):
        """include ENUM_TYPE but also exclude EnumType → empty."""
        res = populated_array.getElementsIE(
            include_data_type=DeclTypes.ENUM_TYPE,
            exclude_identifier="EnumType",
        )
        assert len(res) == 0

    def test_combined_file_path_and_include_type(self, populated_array):
        res = populated_array.getElementsIE(
            file_path="/a.sv",
            include_type=ElementsTypes.MODULE_ELEMENT,
        )
        assert len(res) == 1

    # --- filtered path returns same objects ---

    def test_filter_with_criteria_returns_same_objects(self, populated_array):
        """
        When at least one filter is active, getElementsIE calls addElement(element)
        without copying — so the returned objects must be the same instances.
        """
        res = populated_array.getElementsIE(include_identifier="EnumType")
        original = next(e for e in populated_array if e.identifier == "EnumType")
        assert res[0] is original

    # --- empty array ---

    def test_filter_on_empty_array_returns_empty(self):
        arr = TypedefArray()
        res = arr.getElementsIE(include_data_type=DeclTypes.ENUM_TYPE)
        assert len(res) == 0


# ===========================================================================
# 14. TypedefArray – container protocol
# ===========================================================================

class TestTypedefArrayContainerProtocol:

    def test_len_empty(self):
        assert len(TypedefArray()) == 0

    def test_len_after_add(self):
        arr = make_array(make_typedef())
        assert len(arr) == 1

    def test_iteration_yields_all_elements(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="A", unique_identifier="u1", source_interval=(0, 5)))
        arr.addElement(make_typedef(identifier="B", unique_identifier="u2", source_interval=(6, 10)))
        identifiers = {e.identifier for e in arr}
        assert identifiers == {"A", "B"}

    def test_index_access_returns_element(self):
        arr = make_array(make_typedef(identifier="T"))
        assert arr[0].identifier == "T"

    def test_slice_returns_list(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="A", unique_identifier="u1", source_interval=(0, 5)))
        arr.addElement(make_typedef(identifier="B", unique_identifier="u2", source_interval=(6, 10)))
        arr.addElement(make_typedef(identifier="C", unique_identifier="u3", source_interval=(11, 15)))
        sliced = arr[0:2]
        assert len(sliced) == 2


# ===========================================================================
# 15. TypedefArray – __str__ / __repr__
# ===========================================================================

class TestTypedefArrayRepresentations:

    def test_str_empty_array_is_empty_string(self):
        assert str(TypedefArray()) == ""

    def test_str_single_element_contains_unique_identifier(self):
        arr = make_array(make_typedef(unique_identifier="mod_T"))
        assert "mod_T" in str(arr)

    def test_str_multiple_elements_contains_separator(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="A", unique_identifier="u1", source_interval=(0, 5)))
        arr.addElement(make_typedef(identifier="B", unique_identifier="u2", source_interval=(6, 10)))
        assert ",\n" in str(arr)

    def test_str_contains_both_unique_identifiers(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="A", unique_identifier="uid_A", source_interval=(0, 5)))
        arr.addElement(make_typedef(identifier="B", unique_identifier="uid_B", source_interval=(6, 10)))
        result = str(arr)
        assert "uid_A" in result
        assert "uid_B" in result

    def test_repr_contains_class_name(self):
        assert "TypedefArray" in repr(TypedefArray())

    def test_repr_contains_element_identifier(self):
        arr = make_array(make_typedef(identifier="MyT"))
        assert "MyT" in repr(arr)

    def test_add_element_logs_warning_on_duplicate(self, caplog):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="A", unique_identifier="u1", source_interval=(0, 5)))

        with caplog.at_level(logging.WARNING):
            arr.addElement(make_typedef(identifier="A", unique_identifier="u2", source_interval=(10, 15)))

        assert "It is used!" in caplog.text


BUG_COLLISION_REASON = (
    "BUG: findElementWithSource uses 'or', causing false collisions "
    "when two modules define the same type name with different unique_identifiers."
)

BUG_NONE_REASON = (
    "BUG: replaceTokensWithExpressions calls str(None), producing 'None' in HDL output."
)


class TestTypedefKnownBugs:

    @pytest.mark.xfail(strict=True, reason=BUG_COLLISION_REASON)
    def test_shared_identifier_allows_insertion(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="state_t", unique_identifier="modA_state_t", source_interval=(0, 5)))

        success, _ = arr.addElement(
            make_typedef("state_t", "modB_state_t", (6, 10))
        )

        assert success is True

    @pytest.mark.xfail(strict=True, reason=BUG_COLLISION_REASON)
    def test_shared_identifier_preserves_both_elements(self):
        arr = TypedefArray()
        arr.addElement(make_typedef(identifier="state_t", unique_identifier="modA_state_t", source_interval=(0, 5)))
        arr.addElement(make_typedef(identifier="state_t", unique_identifier="modB_state_t", source_interval=(6, 10)))

        assert len(arr) == 2

    @pytest.mark.xfail(strict=True, reason=BUG_NONE_REASON)
    def test_enum_member_with_no_expression_keeps_original_token(self):
        td = make_typedef(data_type=DeclTypes.ENUM_TYPE)

        td.declarations.addElement(
            Declaration(
                data_type=DeclTypes.ENUM_TYPE,
                identifier="IDLE",
                expression=None,
                source_interval=(0, 1),
            )
        )

        result = td.replaceTokensWithExpressions(["IDLE"])
        assert result == ["IDLE"]

