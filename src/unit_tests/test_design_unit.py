"""
Unit tests for DesignUnit and DesignUnitArray.

Notes on test design:
- Section 19 (getElementsIE) has an intentional asymmetry documented inline:
  the no-filter path returns deep copies (via self.copy()), while the filtered
  path returns original references. The no-filter behaviour is correct; the
  filtered path is a known bug documented in Section 22.
- Counter-based tests (e.g. test_struct_counter_increments_between_instances)
  use du2.number > du1.number rather than du2.number == du1.number + 1 because
  the counters are class-level singletons shared across the entire test session.
- Sections 4, 5, 14 are marked xfail at class level because DesignUnit.copy()
  and copyPart() pass self.number as a 6th positional argument to __init__,
  which only accepts 4. Every test in those classes crashes with TypeError.
  The empty-array copy test is intentionally kept outside the xfail class
  because an empty array never calls element.copy() and would become XPASS.
"""

import pytest
from ..classes.design_unit import DesignUnit, DesignUnitArray
from ..classes.element_types import ElementsTypes
from ..classes.basic import Basic, BasicArray
from ..classes.declarations import Declaration, DeclTypes
from ..classes.value_parametrs import ValueParametr
from ..classes.typedef import Typedef

# ---------------------------------------------------------------------------
# Bug description strings — referenced by xfail markers throughout the file.
# ---------------------------------------------------------------------------

BUG_COPY_NUMBER_ARG = (
    "BUG: DesignUnit.copy() and copyPart() pass self.number as a 6th "
    "positional argument to DesignUnit.__init__(), which only accepts 4. "
    "This raises TypeError at runtime. Fix: remove self.number from the "
    "constructor call — it is already assigned explicitly on the next line."
)

BUG_COPY_PART_MISSING_TYPEDEFS = (
    "BUG: copyPart() does not copy typedefs or input_parametrs. "
    "The comment in the source explicitly notes this omission: "
    "'Missing typedefs and input_parametrs from shallow copy'. "
    "Callers relying on copyPart() for a full shallow copy will silently "
    "get fresh empty arrays for these two collections instead of references."
)

BUG_FILTER_RETURNS_REFERENCES = (
    "BUG: DesignUnitArray.getElementsIE() with filters appends original "
    "element references, not copies. Mutating the result silently mutates "
    "the source array. Inconsistent with the no-filter path which returns "
    "deep copies via self.copy()."
)

# ===========================================================================
# Helpers
# ===========================================================================

def make_du(
    identifier="MyMod",
    source_interval=(0, 10),
    ident_uniq_name="my_mod",
    element_type=ElementsTypes.MODULE_ELEMENT,
) -> DesignUnit:
    return DesignUnit(identifier, source_interval, ident_uniq_name, element_type)


def make_du_array(*units: DesignUnit) -> DesignUnitArray:
    arr = DesignUnitArray()
    for u in units:
        arr.addElement(u)
    return arr


def make_declaration(
    identifier="sig",
    data_type=DeclTypes.LOGIC,
    source_interval=(0, 5),
) -> Declaration:
    """
    Construct a Declaration passing only the arguments the constructor
    requires. If Declaration.__init__ accepts name_space_level, add it back.
    """
    return Declaration(
        data_type=data_type,
        identifier=identifier,
        source_interval=source_interval,
    )


def make_parametr(identifier="clk", param_type="input", source_interval=(0, 3)):
    """Helper that always supplies the required param_type argument."""
    from ..classes.parametrs import Parametr
    return Parametr(
        identifier=identifier,
        param_type=param_type,
        source_interval=source_interval,
    )


# ===========================================================================
# 1. DesignUnit – __init__
# ===========================================================================

class TestDesignUnitInit:

    def test_identifier_uppercased(self):
        du = make_du(identifier="mymod")
        assert du.identifier == "MYMOD"

    def test_identifier_already_upper_unchanged(self):
        du = make_du(identifier="MYMOD")
        assert du.identifier == "MYMOD"

    def test_source_interval_is_stored(self):
        du = make_du(source_interval=(5, 20))
        assert du.source_interval == (5, 20)

    def test_ident_uniq_name_is_stored(self):
        du = make_du(ident_uniq_name="pkg_MyMod")
        assert du.ident_uniq_name == "pkg_MyMod"

    def test_element_type_is_stored(self):
        du = make_du(element_type=ElementsTypes.CLASS_ELEMENT)
        assert du.element_type is ElementsTypes.CLASS_ELEMENT

    def test_default_element_type_is_module_element(self):
        du = DesignUnit()
        assert du.element_type is ElementsTypes.MODULE_ELEMENT

    def test_identifier_upper_cache_matches_identifier(self):
        du = make_du(identifier="mymod")
        assert du.identifier_upper == du.identifier

    def test_ident_uniq_name_upper_is_uppercased(self):
        du = make_du(ident_uniq_name="pkg_MyMod")
        assert du.ident_uniq_name_upper == "PKG_MYMOD"

    def test_number_is_assigned_from_struct_counter(self):
        du = make_du()
        assert isinstance(du.number, int)

    def test_struct_counter_increments_between_instances(self):
        # Counters are class-level singletons; assert ordering only, not a
        # fixed increment, because other tests may create DesignUnits between
        # these two assignments.
        du1 = make_du()
        du2 = make_du()
        assert du2.number > du1.number

    def test_declarations_starts_empty(self):
        assert len(make_du().declarations) == 0

    def test_typedefs_starts_empty(self):
        assert len(make_du().typedefs) == 0

    def test_actions_starts_empty(self):
        assert len(make_du().actions) == 0

    def test_structures_starts_empty(self):
        assert len(make_du().structures) == 0

    def test_out_of_block_elements_starts_empty(self):
        assert len(make_du().out_of_block_elements) == 0

    def test_value_parametrs_starts_empty(self):
        assert len(make_du().value_parametrs) == 0

    def test_input_parametrs_starts_empty(self):
        assert len(make_du().input_parametrs) == 0

    def test_processed_elements_starts_empty(self):
        assert len(make_du().processed_elements) == 0

    def test_tasks_starts_empty(self):
        assert len(make_du().tasks) == 0

    def test_packages_and_objects_starts_empty(self):
        assert len(make_du().packages_and_objects) == 0

    def test_inherits_from_basic(self):
        assert isinstance(make_du(), Basic)


# ===========================================================================
# 2. DesignUnit – setSourceInterval()
# ===========================================================================

class TestDesignUnitSetSourceInterval:

    def test_updates_source_interval(self):
        du = make_du(source_interval=(0, 5))
        du.setSourceInterval((10, 20))
        assert du.source_interval == (10, 20)

    def test_repeated_calls_use_last_value(self):
        du = make_du()
        du.setSourceInterval((1, 2))
        du.setSourceInterval((99, 100))
        assert du.source_interval == (99, 100)

    def test_other_fields_unaffected_by_set_source_interval(self):
        du = make_du(identifier="MOD", ident_uniq_name="u_mod")
        du.setSourceInterval((5, 10))
        assert du.identifier == "MOD"
        assert du.ident_uniq_name == "u_mod"


# ===========================================================================
# 3. DesignUnit – setIdentifier()
# ===========================================================================

class TestDesignUnitSetIdentifier:

    def test_identifier_is_uppercased(self):
        du = make_du()
        du.setIdentifier("newmod", "pkg_newmod")
        assert du.identifier == "NEWMOD"

    def test_ident_uniq_name_is_updated(self):
        du = make_du()
        du.setIdentifier("newmod", "pkg_newmod")
        assert du.ident_uniq_name == "pkg_newmod"

    def test_identifier_upper_cache_is_updated(self):
        du = make_du()
        du.setIdentifier("newmod", "pkg_newmod")
        assert du.identifier_upper == "NEWMOD"

    def test_ident_uniq_name_upper_cache_is_updated(self):
        du = make_du()
        du.setIdentifier("newmod", "pkg_newmod")
        assert du.ident_uniq_name_upper == "PKG_NEWMOD"

    def test_source_interval_unaffected_by_set_identifier(self):
        du = make_du(source_interval=(3, 7))
        du.setIdentifier("other", "other_uid")
        assert du.source_interval == (3, 7)


# ===========================================================================
# 4. DesignUnit – copyPart()
#
# The entire class is xfail because copyPart() passes self.number as a 6th
# positional argument to DesignUnit.__init__(), causing TypeError on every
# call. Once BUG_COPY_NUMBER_ARG is fixed the class marker must be removed.
#
# Note: test_copy_part_does_not_raise lives in Section 4b (its own class)
# because its intent — "must NOT raise" — is the logical inverse of the
# class-level xfail. Placing it here would mislead readers.
# ===========================================================================

@pytest.mark.xfail(strict=True, raises=TypeError, reason=BUG_COPY_NUMBER_ARG)
class TestDesignUnitCopyPart:

    def test_copy_part_returns_different_object(self):
        du = make_du()
        assert du.copyPart() is not du

    def test_copy_part_returns_design_unit_instance(self):
        du = make_du()
        assert isinstance(du.copyPart(), DesignUnit)

    def test_copy_part_shares_declarations_reference(self):
        du = make_du()
        copied = du.copyPart()
        assert copied.declarations is du.declarations

    def test_copy_part_shares_actions_reference(self):
        du = make_du()
        copied = du.copyPart()
        assert copied.actions is du.actions

    def test_copy_part_shares_structures_reference(self):
        du = make_du()
        copied = du.copyPart()
        assert copied.structures is du.structures

    def test_copy_part_shares_value_parametrs_reference(self):
        du = make_du()
        copied = du.copyPart()
        assert copied.value_parametrs is du.value_parametrs

    def test_copy_part_shares_out_of_block_elements_reference(self):
        du = make_du()
        copied = du.copyPart()
        assert copied.out_of_block_elements is du.out_of_block_elements

    def test_copy_part_shares_processed_elements_reference(self):
        du = make_du()
        copied = du.copyPart()
        assert copied.processed_elements is du.processed_elements

    def test_copy_part_shares_tasks_reference(self):
        du = make_du()
        copied = du.copyPart()
        assert copied.tasks is du.tasks

    def test_copy_part_shares_packages_and_objects_reference(self):
        du = make_du()
        copied = du.copyPart()
        assert copied.packages_and_objects is du.packages_and_objects

    def test_copy_part_preserves_number(self):
        du = make_du()
        copied = du.copyPart()
        assert copied.number == du.number


# ===========================================================================
# 4b. copyPart() regression guard
#
# Kept in its own class so the "must not raise" intent is not hidden under
# the class-level xfail of Section 4. After BUG_COPY_NUMBER_ARG is fixed
# this test should pass cleanly and the xfail marker must be removed.
# ===========================================================================

class TestDesignUnitCopyPartRegression:

    @pytest.mark.xfail(strict=True, raises=TypeError, reason=BUG_COPY_NUMBER_ARG)
    def test_copy_part_does_not_raise(self):
        """
        Regression: copyPart() passes self.number as a 6th positional arg to
        DesignUnit.__init__(), which only accepts 4, raising TypeError.
        This xfail will become XPASS once the source is fixed, signalling
        that this marker and the surrounding section can be removed.
        """
        du = make_du()
        du.copyPart()


# ===========================================================================
# 5. DesignUnit – copy()
#
# Same class-level xfail rationale as Section 4.
# ===========================================================================

@pytest.mark.xfail(strict=True, raises=TypeError, reason=BUG_COPY_NUMBER_ARG)
class TestDesignUnitCopy:

    def test_copy_returns_different_object(self):
        du = make_du()
        assert du.copy() is not du

    def test_copy_returns_design_unit_instance(self):
        du = make_du()
        assert isinstance(du.copy(), DesignUnit)

    def test_copy_preserves_identifier(self):
        du = make_du(identifier="MOD")
        assert du.copy().identifier == "MOD"

    def test_copy_preserves_ident_uniq_name(self):
        du = make_du(ident_uniq_name="pkg_mod")
        assert du.copy().ident_uniq_name == "pkg_mod"

    def test_copy_preserves_source_interval(self):
        du = make_du(source_interval=(3, 9))
        assert du.copy().source_interval == (3, 9)

    def test_copy_preserves_element_type(self):
        du = make_du(element_type=ElementsTypes.CLASS_ELEMENT)
        assert du.copy().element_type is ElementsTypes.CLASS_ELEMENT

    def test_copy_declarations_is_different_object(self):
        du = make_du()
        assert du.copy().declarations is not du.declarations

    def test_copy_typedefs_is_different_object(self):
        du = make_du()
        assert du.copy().typedefs is not du.typedefs

    def test_copy_value_parametrs_is_different_object(self):
        du = make_du()
        assert du.copy().value_parametrs is not du.value_parametrs

    def test_copy_declarations_mutation_does_not_affect_original(self):
        du = make_du()
        du.declarations.addElement(make_declaration("sig_a"))
        copied = du.copy()
        copied.declarations.addElement(
            make_declaration("sig_b", source_interval=(6, 10))
        )
        assert len(du.declarations) == 1

    def test_copy_preserves_number(self):
        du = make_du()
        assert du.copy().number == du.number


# ===========================================================================
# 5b. copy() regression guard — same pattern as Section 4b.
# ===========================================================================

class TestDesignUnitCopyRegression:

    @pytest.mark.xfail(strict=True, raises=TypeError, reason=BUG_COPY_NUMBER_ARG)
    def test_copy_does_not_raise(self):
        """
        Regression: copy() passes self.number as a 6th positional arg to
        DesignUnit.__init__(), which only accepts 4, raising TypeError.
        This xfail will become XPASS once the source is fixed.
        """
        du = make_du()
        du.copy()


# ===========================================================================
# 6. DesignUnit – isIncludeOutOfBlockElements()
# ===========================================================================

class TestDesignUnitIsIncludeOutOfBlockElements:

    def test_returns_false_when_empty(self):
        assert make_du().isIncludeOutOfBlockElements() is False

    def test_returns_true_when_not_empty(self):
        from ..classes.protocols import Protocol
        du = make_du()
        proto = Protocol(
            identifier="p1",
            source_interval=(0, 5),
            element_type=ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
        )
        du.out_of_block_elements.addElement(proto)
        assert du.isIncludeOutOfBlockElements() is True


# ===========================================================================
# 7. DesignUnit – getInputParametrs()
# ===========================================================================

class TestDesignUnitGetInputParametrs:

    def test_returns_empty_string_when_no_params(self):
        assert make_du().getInputParametrs() == ""

    def test_returns_parenthesized_string_containing_identifier(self):
        """Single test covers both the parentheses format and identifier presence."""
        du = make_du()
        du.input_parametrs.addElement(make_parametr("clk"))
        result = du.getInputParametrs()
        assert result.startswith("(")
        assert result.endswith(")")
        assert "clk" in result

    def test_multiple_params_all_appear_in_result(self):
        du = make_du()
        du.input_parametrs.addElement(make_parametr("clk", source_interval=(0, 3)))
        du.input_parametrs.addElement(
            make_parametr("rst", param_type="input", source_interval=(4, 7))
        )
        result = du.getInputParametrs()
        assert "clk" in result
        assert "rst" in result


# ===========================================================================
# 8. DesignUnit – findElementByIdentifier()
# ===========================================================================

class TestDesignUnitFindElementByIdentifier:

    def test_finds_typedef_by_identifier(self):
        du = make_du()
        td = Typedef(
            identifier="state_t",
            unique_identifier="mod_state_t",
            source_interval=(0, 5),
            file_path="/f.sv",
            data_type=DeclTypes.ENUM_TYPE,
        )
        du.typedefs.addElement(td)
        result = du.findElementByIdentifier("state_t")
        assert any(r is td for r in result)

    def test_finds_declaration_by_identifier(self):
        du = make_du()
        decl = make_declaration("wire_a")
        du.declarations.addElement(decl)
        result = du.findElementByIdentifier("wire_a")
        assert any(r is decl for r in result)

    def test_finds_value_parametr_by_identifier(self):
        du = make_du()
        vp = ValueParametr("WIDTH", (0, 5), value=8)
        du.value_parametrs.addElement(vp)
        result = du.findElementByIdentifier("WIDTH")
        assert any(r.identifier == "WIDTH" for r in result)

    def test_returns_empty_list_when_not_found(self):
        result = make_du().findElementByIdentifier("NONEXISTENT")
        assert result == []

    def test_returns_list_type(self):
        assert isinstance(make_du().findElementByIdentifier("X"), list)

    def test_declaration_with_expression_includes_action(self):
        """
        Declaration with a non-empty expression and an associated action should
        include that action in the result.
        Note: if Declaration.__init__ does not accept `action` as a keyword
        argument, adjust the constructor call to match the real signature.
        """
        from ..classes.actions import Action
        du = make_du()
        action = Action(
            identifier="act_a",
            source_interval=(0, 5),
            element_type=ElementsTypes.ASSIGN_ELEMENT,
        )
        decl = Declaration(
            data_type=DeclTypes.LOGIC,
            identifier="wire_a",
            expression="1",
            source_interval=(0, 5),
            action=action,
        )
        du.declarations.addElement(decl)
        result = du.findElementByIdentifier("wire_a")
        assert action in result

    def test_declaration_without_expression_does_not_include_action(self):
        from ..classes.actions import Action
        du = make_du()
        action = Action(
            identifier="act_a",
            source_interval=(0, 5),
            element_type=ElementsTypes.ASSIGN_ELEMENT,
        )
        decl = Declaration(
            data_type=DeclTypes.LOGIC,
            identifier="wire_a",
            expression="",
            source_interval=(0, 5),
            action=action,
        )
        du.declarations.addElement(decl)
        result = du.findElementByIdentifier("wire_a")
        assert action not in result

    def test_enum_type_declaration_does_not_include_action(self):
        from ..classes.actions import Action
        du = make_du()
        action = Action(
            identifier="act_e",
            source_interval=(0, 5),
            element_type=ElementsTypes.ASSIGN_ELEMENT,
        )
        decl = Declaration(
            data_type=DeclTypes.ENUM_TYPE,
            identifier="color_t",
            expression="RED",
            source_interval=(0, 5),
            action=action,
        )
        du.declarations.addElement(decl)
        result = du.findElementByIdentifier("color_t")
        assert action not in result

    def test_finds_task_by_identifier(self):
        from ..classes.tasks import Task
        du = make_du()
        task = Task(
            identifier="my_task",
            source_interval=(0, 10),
            namespace_level=0,
            element_type=ElementsTypes.TASK_ELEMENT,
        )
        du.tasks.addElement(task)
        result = du.findElementByIdentifier("my_task")
        assert any(r is task for r in result)

    def test_task_with_structure_appends_structure(self):
        """findElementByIdentifier also appends task.structure when present."""
        from ..classes.tasks import Task
        from ..classes.structure import Structure
        du = make_du()
        task = Task(
            identifier="my_task",
            source_interval=(0, 10),
            namespace_level=0,
            element_type=ElementsTypes.TASK_ELEMENT,
        )
        struct = Structure(
            identifier="my_task_struct",
            source_interval=(0, 10),
            element_type=ElementsTypes.TASK_ELEMENT,
        )
        task.structure = struct
        du.tasks.addElement(task)
        result = du.findElementByIdentifier("my_task")
        assert struct in result

    def test_task_without_structure_does_not_crash(self):
        """A task whose structure is None must not raise when searched."""
        from ..classes.tasks import Task
        du = make_du()
        task = Task(
            identifier="bare_task",
            source_interval=(0, 5),
            namespace_level=0,
        )
        du.tasks.addElement(task)
        result = du.findElementByIdentifier("bare_task")
        assert any(r is task for r in result)


# ===========================================================================
# 9. DesignUnit – findAndChangeNamesToAgentAttrCall()
# ===========================================================================

class TestDesignUnitFindAndChangeNamesToAgentAttrCall:

    def test_module_element_uses_ident_uniq_name_prefix(self):
        du = make_du(
            ident_uniq_name="my_mod", element_type=ElementsTypes.MODULE_ELEMENT
        )
        du.declarations.addElement(make_declaration("sig"))
        result = du.findAndChangeNamesToAgentAttrCall("sig")
        assert "my_mod.sig" in result

    def test_class_element_uses_object_pointer_prefix(self):
        du = make_du(element_type=ElementsTypes.CLASS_ELEMENT)
        du.declarations.addElement(make_declaration("field"))
        result = du.findAndChangeNamesToAgentAttrCall("field")
        assert "object_pointer.field" in result

    def test_unknown_identifier_is_unchanged(self):
        du = make_du()
        result = du.findAndChangeNamesToAgentAttrCall("unknown_sig")
        assert result == "unknown_sig"

    def test_package_declarations_are_substituted(self):
        du = make_du(ident_uniq_name="top", element_type=ElementsTypes.MODULE_ELEMENT)
        pkg = make_du(
            ident_uniq_name="pkg", element_type=ElementsTypes.PACKAGE_ELEMENT
        )
        pkg.declarations.addElement(make_declaration("pkg_sig"))
        result = du.findAndChangeNamesToAgentAttrCall("pkg_sig", packages=[pkg])
        assert "pkg.pkg_sig" in result

    def test_class_element_with_package_uses_object_pointer(self):
        du = make_du(element_type=ElementsTypes.CLASS_ELEMENT)
        pkg = make_du(ident_uniq_name="pkg")
        pkg.declarations.addElement(make_declaration("pkg_field"))
        result = du.findAndChangeNamesToAgentAttrCall("pkg_field", packages=[pkg])
        assert "object_pointer.pkg_field" in result

    def test_packages_none_does_not_crash(self):
        du = make_du()
        result = du.findAndChangeNamesToAgentAttrCall("anything", packages=None)
        assert isinstance(result, str)

    def test_packages_empty_list_does_not_crash(self):
        """packages=[] is a distinct code path from packages=None."""
        du = make_du()
        result = du.findAndChangeNamesToAgentAttrCall("anything", packages=[])
        assert isinstance(result, str)

    def test_word_boundary_prevents_partial_replacement(self):
        du = make_du(ident_uniq_name="mod")
        du.declarations.addElement(make_declaration("sig"))
        result = du.findAndChangeNamesToAgentAttrCall("signal")
        assert "mod.sig" not in result


# ===========================================================================
# 10. DesignUnit – getBehInitProtocols()
# ===========================================================================

class TestDesignUnitGetBehInitProtocols:

    def test_returns_string(self):
        assert isinstance(make_du().getBehInitProtocols(), str)

    def test_empty_design_unit_returns_empty_string(self):
        assert make_du().getBehInitProtocols() == ""

    def test_declaration_with_expression_appears_in_output(self):
        du = make_du(ident_uniq_name="mod")
        du.declarations.addElement(
            Declaration(
                data_type=DeclTypes.LOGIC,
                identifier="sig",
                expression="1",
                source_interval=(0, 5),
            )
        )
        result = du.getBehInitProtocols()
        assert "1" in result

    def test_init_protocol_name_contains_ident_uniq_name(self):
        du = make_du(ident_uniq_name="my_mod")
        du.declarations.addElement(
            Declaration(
                data_type=DeclTypes.LOGIC,
                identifier="sig",
                expression="0",
                source_interval=(0, 5),
            )
        )
        result = du.getBehInitProtocols()
        assert "MY_MOD" in result

    def test_result_does_not_end_with_trailing_newline(self):
        du = make_du(ident_uniq_name="mod")
        du.declarations.addElement(
            Declaration(
                data_type=DeclTypes.LOGIC,
                identifier="sig",
                expression="1",
                source_interval=(0, 5),
            )
        )
        assert not du.getBehInitProtocols().endswith("\n")

    def test_out_of_block_protocol_triggers_main_section(self):
        """
        Adding a Protocol to out_of_block_elements exercises
        _format_main_protocol_section without needing full Structure objects.
        Both the protocol identifier and the MAIN_ prefix must appear.
        """
        from ..classes.protocols import Protocol
        du = make_du(ident_uniq_name="oob_mod")
        du.out_of_block_elements.addElement(
            Protocol(
                identifier="oob_proto",
                source_interval=(0, 5),
                element_type=ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
            )
        )
        result = du.getBehInitProtocols()
        assert isinstance(result, str)
        assert "oob_proto" in result
        assert "MAIN_" in result

    def test_both_declaration_and_out_of_block_produce_combined_output(self):
        """
        When both a declaration with an expression and an out_of_block Protocol
        are present, the output must contain both INIT and MAIN sections.
        """
        from ..classes.protocols import Protocol
        du = make_du(ident_uniq_name="combined_mod")
        du.declarations.addElement(
            Declaration(
                data_type=DeclTypes.LOGIC,
                identifier="sig",
                expression="1",
                source_interval=(0, 5),
            )
        )
        du.out_of_block_elements.addElement(
            Protocol(
                identifier="main_proto",
                source_interval=(0, 5),
                element_type=ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT,
            )
        )
        result = du.getBehInitProtocols()
        assert "INIT_" in result
        assert "MAIN_" in result
        assert "main_proto" in result


# ===========================================================================
# 11. DesignUnit – __repr__
# ===========================================================================

class TestDesignUnitRepr:

    def test_repr_contains_class_name(self):
        assert "DesignUnit(" in repr(make_du())

    def test_repr_contains_identifier(self):
        assert "MYMOD" in repr(make_du(identifier="mymod"))

    def test_repr_contains_ident_uniq_name(self):
        assert "'my_mod'" in repr(make_du(ident_uniq_name="my_mod"))

    def test_repr_contains_source_interval(self):
        assert "(0, 10)" in repr(make_du(source_interval=(0, 10)))

    def test_repr_contains_element_type(self):
        assert "MODULE_ELEMENT" in repr(make_du())


# ===========================================================================
# 12. DesignUnitArray – __init__
# ===========================================================================

class TestDesignUnitArrayInit:

    def test_element_type_is_design_unit(self):
        assert DesignUnitArray().element_type is DesignUnit

    def test_starts_empty(self):
        assert len(DesignUnitArray()) == 0

    def test_inherits_from_basic_array(self):
        assert isinstance(DesignUnitArray(), BasicArray)


# ===========================================================================
# 13. DesignUnitArray – addElement()
# ===========================================================================

class TestDesignUnitArrayAddElement:

    def test_element_present_after_add(self):
        arr = DesignUnitArray()
        du = make_du(identifier="A", ident_uniq_name="u_a")
        arr.addElement(du)
        assert any(e.ident_uniq_name == "u_a" for e in arr)

    def test_length_increases_after_add(self):
        arr = DesignUnitArray()
        arr.addElement(make_du())
        assert len(arr) == 1

    def test_returns_index_of_added_element(self):
        arr = DesignUnitArray()
        idx = arr.addElement(make_du())
        assert isinstance(idx, int)


# ===========================================================================
# 13b. DesignUnitArray.copy() on an empty array
#
# Kept outside Section 14 (which is xfail for TypeError) because copy() on
# an empty array never calls element.copy(), so TypeError is never raised.
# With strict=True the test would become XPASS, causing a spurious failure.
# ===========================================================================

def test_copy_of_empty_array_is_empty():
    assert len(DesignUnitArray().copy()) == 0


# ===========================================================================
# 14. DesignUnitArray – copy()
#
# Class-level xfail: DesignUnitArray.copy() calls element.copy() which hits
# the same BUG_COPY_NUMBER_ARG TypeError as DesignUnit.copy().
# The empty-array case lives in Section 13b above.
# ===========================================================================

@pytest.mark.xfail(strict=True, raises=TypeError, reason=BUG_COPY_NUMBER_ARG)
class TestDesignUnitArrayCopy:

    def test_copy_does_not_raise(self):
        """Regression: copy() calls element.copy() which crashes."""
        arr = make_du_array(make_du(ident_uniq_name="u_reg"))
        arr.copy()

    def test_copy_returns_different_array(self):
        arr = make_du_array(make_du(ident_uniq_name="u_a"))
        assert arr.copy() is not arr

    def test_copy_element_is_different_object(self):
        du = make_du(ident_uniq_name="u_b")
        arr = make_du_array(du)
        assert arr.copy()[0] is not du

    def test_copy_preserves_element_count(self):
        arr = make_du_array(
            make_du(identifier="A", ident_uniq_name="u_a"),
            make_du(identifier="B", ident_uniq_name="u_b"),
        )
        assert len(arr.copy()) == 2

    def test_copy_mutation_does_not_affect_original(self):
        arr = make_du_array(make_du(ident_uniq_name="orig"))
        copied = arr.copy()
        copied[0].ident_uniq_name = "mutated"
        assert arr[0].ident_uniq_name == "orig"

    def test_copy_returns_design_unit_array_instance(self):
        arr = make_du_array(make_du(ident_uniq_name="u_c"))
        assert isinstance(arr.copy(), DesignUnitArray)


# ===========================================================================
# 15. DesignUnitArray – findModuleByUniqIdentifier()
# ===========================================================================

class TestDesignUnitArrayFindModuleByUniqIdentifier:

    def test_finds_by_unique_identifier(self):
        du = make_du(ident_uniq_name="target_uid")
        arr = make_du_array(du)
        assert arr.findModuleByUniqIdentifier("target_uid") is du

    def test_returns_none_when_not_found(self):
        arr = make_du_array(make_du(ident_uniq_name="other"))
        assert arr.findModuleByUniqIdentifier("missing") is None

    def test_returns_none_for_empty_array(self):
        assert DesignUnitArray().findModuleByUniqIdentifier("any") is None

    def test_does_not_match_partial_identifier(self):
        arr = make_du_array(make_du(ident_uniq_name="long_uid"))
        assert arr.findModuleByUniqIdentifier("long") is None


# ===========================================================================
# 16. DesignUnitArray – getElement() (inherited from BasicArray)
# ===========================================================================

class TestDesignUnitArrayGetElement:

    def test_finds_by_uppercased_identifier(self):
        """
        BasicArray.getElement() searches by element.identifier, which for
        DesignUnit is always uppercased — the search key must match.
        """
        du = make_du(identifier="mymod", ident_uniq_name="u_mymod")
        arr = make_du_array(du)
        assert arr.getElement("MYMOD") is du

    def test_returns_none_for_missing_identifier(self):
        arr = make_du_array(make_du(identifier="X", ident_uniq_name="u_x"))
        assert arr.getElement("NOTHERE") is None

    def test_lowercase_key_does_not_match_uppercased_identifier(self):
        """
        DesignUnit uppercases its identifier, so a lowercase key will not
        find it. This test documents that behaviour.
        """
        du = make_du(identifier="mymod", ident_uniq_name="u_lc")
        arr = make_du_array(du)
        assert arr.getElement("mymod") is None

    def test_returns_none_for_empty_array(self):
        assert DesignUnitArray().getElement("ANY") is None


# ===========================================================================
# 17. DesignUnitArray – getElementByIndex()
# ===========================================================================

class TestDesignUnitArrayGetElementByIndex:

    def test_retrieves_correct_element(self):
        du = make_du(ident_uniq_name="u0")
        arr = make_du_array(du)
        assert arr.getElementByIndex(0) is du

    def test_raises_index_error_for_empty_array(self):
        with pytest.raises(IndexError):
            DesignUnitArray().getElementByIndex(0)

    def test_raises_index_error_for_out_of_bounds(self):
        arr = make_du_array(make_du(ident_uniq_name="u_oob"))
        with pytest.raises(IndexError):
            arr.getElementByIndex(99)

    def test_returns_design_unit_instance(self):
        arr = make_du_array(make_du(ident_uniq_name="u_inst"))
        assert isinstance(arr.getElementByIndex(0), DesignUnit)


# ===========================================================================
# 18. DesignUnitArray – getElements()
# ===========================================================================

class TestDesignUnitArrayGetElements:

    def test_returns_list(self):
        arr = make_du_array(make_du(ident_uniq_name="u_lst"))
        assert isinstance(arr.getElements(), list)

    def test_returns_all_elements(self):
        arr = make_du_array(
            make_du(identifier="A", ident_uniq_name="u_a"),
            make_du(identifier="B", ident_uniq_name="u_b"),
        )
        assert len(arr.getElements()) == 2

    def test_returns_same_list_reference(self):
        arr = make_du_array(make_du(ident_uniq_name="u_ref"))
        assert arr.getElements() is arr.elements


# ===========================================================================
# 19. DesignUnitArray – getElementsIE()
# ===========================================================================

class TestDesignUnitArrayGetElementsIE:

    @pytest.fixture
    def populated_array(self) -> DesignUnitArray:
        arr = DesignUnitArray()
        arr.addElement(
            make_du(
                identifier="Mod",
                ident_uniq_name="u_mod",
                element_type=ElementsTypes.MODULE_ELEMENT,
            )
        )
        arr.addElement(
            make_du(
                identifier="Cls",
                ident_uniq_name="u_cls",
                element_type=ElementsTypes.CLASS_ELEMENT,
            )
        )
        return arr

    # --- no filters (calls self.copy() → hits BUG_COPY_NUMBER_ARG) ---

    @pytest.mark.xfail(strict=True, raises=TypeError, reason=BUG_COPY_NUMBER_ARG)
    def test_no_filters_returns_design_unit_array(self, populated_array):
        assert isinstance(populated_array.getElementsIE(), DesignUnitArray)

    @pytest.mark.xfail(strict=True, raises=TypeError, reason=BUG_COPY_NUMBER_ARG)
    def test_no_filters_returns_all_elements(self, populated_array):
        assert len(populated_array.getElementsIE()) == 2

    @pytest.mark.xfail(strict=True, raises=TypeError, reason=BUG_COPY_NUMBER_ARG)
    def test_no_filters_returns_new_object(self, populated_array):
        assert populated_array.getElementsIE() is not populated_array

    @pytest.mark.xfail(strict=True, raises=TypeError, reason=BUG_COPY_NUMBER_ARG)
    def test_no_filters_returns_copies_not_same_objects(self, populated_array):
        """
        The no-filter path calls self.copy() → deep-copies every element, so
        returned objects differ from the originals. This is CORRECT behaviour.

        The filtered path is inconsistent: it returns original references.
        That inconsistency is documented as BUG_FILTER_RETURNS_REFERENCES and
        tested by test_filter_with_criteria_returns_same_objects below.
        """
        res = populated_array.getElementsIE()
        assert res[0] is not populated_array[0]

    # --- include ---

    def test_include_returns_matching_element(self, populated_array):
        res = populated_array.getElementsIE(include=ElementsTypes.MODULE_ELEMENT)
        assert any(e.ident_uniq_name == "u_mod" for e in res)

    def test_include_excludes_non_matching(self, populated_array):
        res = populated_array.getElementsIE(include=ElementsTypes.MODULE_ELEMENT)
        assert not any(e.ident_uniq_name == "u_cls" for e in res)

    # --- exclude ---

    def test_exclude_removes_matching(self, populated_array):
        res = populated_array.getElementsIE(exclude=ElementsTypes.MODULE_ELEMENT)
        assert not any(e.ident_uniq_name == "u_mod" for e in res)

    def test_exclude_keeps_non_matching(self, populated_array):
        res = populated_array.getElementsIE(exclude=ElementsTypes.MODULE_ELEMENT)
        assert any(e.ident_uniq_name == "u_cls" for e in res)

    # --- include_ident_uniq_names ---

    def test_include_ident_uniq_names_returns_only_matching(self, populated_array):
        res = populated_array.getElementsIE(include_ident_uniq_names=["u_mod"])
        assert len(res) == 1

    def test_include_ident_uniq_names_correct_element(self, populated_array):
        res = populated_array.getElementsIE(include_ident_uniq_names=["u_mod"])
        assert res[0].ident_uniq_name == "u_mod"

    def test_include_ident_uniq_names_multiple_values(self, populated_array):
        res = populated_array.getElementsIE(
            include_ident_uniq_names=["u_mod", "u_cls"]
        )
        assert len(res) == 2

    # --- exclude_ident_uniq_name ---

    def test_exclude_ident_uniq_name_removes_matching(self, populated_array):
        res = populated_array.getElementsIE(exclude_ident_uniq_name="u_mod")
        assert not any(e.ident_uniq_name == "u_mod" for e in res)

    def test_exclude_ident_uniq_name_keeps_other(self, populated_array):
        res = populated_array.getElementsIE(exclude_ident_uniq_name="u_mod")
        assert any(e.ident_uniq_name == "u_cls" for e in res)

    # --- combined ---

    def test_combined_include_and_exclude_ident_uniq_name_empty(self, populated_array):
        res = populated_array.getElementsIE(
            include=ElementsTypes.MODULE_ELEMENT,
            exclude_ident_uniq_name="u_mod",
        )
        assert len(res) == 0

    # --- filtered path documents the reference-return bug ---

    @pytest.mark.xfail(strict=True, reason=BUG_FILTER_RETURNS_REFERENCES)
    def test_filtered_result_mutation_does_not_affect_original(self, populated_array):
        """
        Correct behaviour: mutating a filtered result must not affect the
        source array. Currently broken — the filtered path returns original
        references. xfail will become XPASS when fixed.
        """
        res = populated_array.getElementsIE(include_ident_uniq_names=["u_mod"])
        res[0].ident_uniq_name = "MUTATED"
        assert populated_array[0].ident_uniq_name != "MUTATED"

    def test_filter_with_criteria_returns_same_objects(self, populated_array):
        """
        Documents the current (buggy) behaviour: the filtered path returns
        original element references rather than copies. This test will fail
        once BUG_FILTER_RETURNS_REFERENCES is fixed; remove it at that point
        together with the xfail above.
        """
        res = populated_array.getElementsIE(include_ident_uniq_names=["u_mod"])
        original = next(
            e for e in populated_array if e.ident_uniq_name == "u_mod"
        )
        assert res[0] is original

    # --- empty array ---

    def test_filter_on_empty_array_returns_empty(self):
        res = DesignUnitArray().getElementsIE(include=ElementsTypes.MODULE_ELEMENT)
        assert len(res) == 0


# ===========================================================================
# 20. DesignUnitArray – container protocol
# ===========================================================================

class TestDesignUnitArrayContainerProtocol:

    def test_len_empty(self):
        assert len(DesignUnitArray()) == 0

    def test_len_after_add(self):
        arr = make_du_array(make_du(ident_uniq_name="u_len"))
        assert len(arr) == 1

    def test_iteration_yields_all_elements(self):
        arr = make_du_array(
            make_du(identifier="A", ident_uniq_name="u_a"),
            make_du(identifier="B", ident_uniq_name="u_b"),
        )
        assert {e.ident_uniq_name for e in arr} == {"u_a", "u_b"}

    def test_index_access_returns_element(self):
        du = make_du(ident_uniq_name="u_idx")
        arr = make_du_array(du)
        assert arr[0] is du

    def test_slice_returns_list(self):
        arr = make_du_array(
            make_du(identifier="A", ident_uniq_name="u_s_a"),
            make_du(identifier="B", ident_uniq_name="u_s_b"),
            make_du(identifier="C", ident_uniq_name="u_s_c"),
        )
        assert len(arr[0:2]) == 2


# ===========================================================================
# 21. DesignUnitArray – __repr__
# ===========================================================================

class TestDesignUnitArrayRepr:

    def test_repr_contains_class_name(self):
        assert "DesignUnitArray" in repr(DesignUnitArray())

    def test_repr_contains_element_identifier(self):
        arr = make_du_array(make_du(identifier="MYMOD", ident_uniq_name="u_mymod"))
        assert "MYMOD" in repr(arr)


# ===========================================================================
# 22. Known bugs
# ===========================================================================

class TestDesignUnitKnownBugs:

    @pytest.mark.xfail(strict=True, raises=TypeError, reason=BUG_COPY_PART_MISSING_TYPEDEFS)
    def test_copy_part_shares_typedefs_reference(self):
        """
        copyPart() omits typedefs from its shallow copy. Currently the test
        also crashes with TypeError (BUG_COPY_NUMBER_ARG), so raises=TypeError
        reflects the actual failure mode. Once BUG_COPY_NUMBER_ARG is fixed,
        change raises to AssertionError (or remove once typedefs sharing is
        also fixed).
        """
        du = make_du()
        copied = du.copyPart()
        assert copied.typedefs is du.typedefs

    @pytest.mark.xfail(strict=True, raises=TypeError, reason=BUG_COPY_PART_MISSING_TYPEDEFS)
    def test_copy_part_shares_input_parametrs_reference(self):
        """Same note as test_copy_part_shares_typedefs_reference above."""
        du = make_du()
        copied = du.copyPart()
        assert copied.input_parametrs is du.input_parametrs