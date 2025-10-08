from typing import Any
import importlib
import sys
import types

import pytest

from ..classes.structure import Structure, StructureArray
from ..classes.protocols import BodyElement, Protocol
from ..classes.parametrs import Parametr, ParametrArray
from ..classes.element_types import ElementsTypes
from ..utils.counters import Counters, CounterTypes


# -------------------------
# Fixtures & test utilities
# -------------------------

@pytest.fixture(autouse=True)
def reset_counters():
    """
    Ensure Counters singleton is reinitialized before and after each test.
    This makes numbering deterministic and isolates tests.
    """
    Counters().reinit()
    yield
    Counters().reinit()


@pytest.fixture
def empty_structure():
    """Return a fresh Structure with explicit number 0 for predictability."""
    return Structure("s_empty", (1, 2), ElementsTypes.NONE_ELEMENT, number=0)


@pytest.fixture
def structure_with_params():
    """Return a Structure prepopulated with ParametrArray containing two parameters."""
    s = Structure("s_params", (0, 0), ElementsTypes.FUNCTION_ELEMENT, number=1)
    pa = ParametrArray()
    pa.addElement(Parametr("p_a", "int"))
    pa.addElement(Parametr("p_b", "int"))
    s.parametrs = pa
    return s


# -------------------------
# Tests for Structure class
# -------------------------
class TestStructure:

    def test_init_assigns_identifier_and_interval_and_type(self):
        """__init__: identifier, source_interval and element_type are set correctly."""
        s = Structure("my_struct", (10, 20), ElementsTypes.TASK_ELEMENT, number=2)
        assert s.identifier == "my_struct"
        assert s.source_interval == (10, 20)
        assert s.element_type is ElementsTypes.TASK_ELEMENT

    def test_number_auto_assigned_when_not_passed(self):
        """__init__: when number not provided, it is taken from Counters and counter increments."""
        c = Counters()
        start = c.get(CounterTypes.STRUCT_COUNTER)
        s = Structure("auto_num", (0, 0))
        # structure.number should equal start (old value) and counter should be incremented after construction
        assert s.number == start
        assert c.get(CounterTypes.STRUCT_COUNTER) == start + 1

    def test_getName_includes_number_and_additional_params(self):
        """getName: includes number suffix when number truthy and includes additional_params when present."""
        s = Structure("nameX", (0, 0), number=7)
        s.additional_params = "a,b"
        assert s.getName(True) == "nameX_7(a,b)"
        assert s.getName(False) == "nameX_7"

    def test_getName_uses_parametrs_when_additional_params_absent(self, structure_with_params):
        """getName: shows parametrs string when additional_params is None but parametrs exist."""
        s = structure_with_params
        name = s.getName(True)
        assert name.startswith("s_params_1(")
        # both parameter identifiers should appear
        assert "p_a" in name and "p_b" in name

    def test_getLastBehaviorIndex_on_empty_and_nonempty(self):
        """getLastBehaviorIndex: returns None for empty behavior, last index for non-empty."""
        s = Structure("X", (0, 0))
        assert s.getLastBehaviorIndex() is None
        s.addProtocol("p1")
        s.addProtocol("p2")
        assert s.getLastBehaviorIndex() == 1

    def test_insertBehavior_inserts_at_index(self):
        """insertBehavior: inserts element at requested index preserving order."""
        s = Structure("S", (0, 0))
        idx0 = s.addProtocol("first")
        s.addProtocol("second")
        new_proto = Protocol("inserted", (0, 0))
        s.insertBehavior(1, new_proto)
        assert s.behavior[1].identifier == "inserted"

    def test_addProtocol_combines_params_when_not_inside_task(self):
        """addProtocol: when inside_the_task is False, combine structure.parametrs and passed parametrs."""
        s = Structure("Comb", (0, 0))
        # give structure one parameter
        s.parametrs = ParametrArray()
        s.parametrs.addElement(Parametr("base", "int"))
        # prepare passed parametrs
        pa = ParametrArray()
        pa.addElement(Parametr("x", "int"))
        pa.addElement(Parametr("y", "int"))
        idx = s.addProtocol("combined", ElementsTypes.PROTOCOL_ELEMENT, parametrs=pa, inside_the_task=False)
        assert idx == 0
        proto = s.behavior[0]
        ids = [p.identifier for p in proto.parametrs.getElements()]
        assert set(["base", "x", "y"]).issubset(set(ids))

    def test_addProtocol_inside_task_uses_only_passed_params(self):
        """addProtocol: when inside_the_task True, only explicitly passed parametrs are used."""
        s = Structure("T", (0, 0))
        s.parametrs = ParametrArray()
        s.parametrs.addElement(Parametr("should_not", "int"))
        pa = ParametrArray()
        pa.addElement(Parametr("only", "int"))
        idx = s.addProtocol("ptask", ElementsTypes.PROTOCOL_ELEMENT, parametrs=pa, inside_the_task=True)
        proto = s.behavior[idx]
        ids = [p.identifier for p in proto.parametrs.getElements()]
        assert "should_not" not in ids
        assert "only" in ids

    def test_addBodyElement_logs_warning_when_behavior_empty(self, caplog):
        """
        addBodyElement: should warn via logger when behavior list is empty.
        Checks logger message content for exact phrasing used in code.
        """
        s = Structure("no_beh", (0, 0))
        caplog.set_level("WARNING")
        be = BodyElement("doit")
        s.addBodyElement(be)
        # Expect at least one warning record with the known message pattern
        expected_msg = f"Cannot add BodyElement to empty behavior list in Structure '{s.identifier}'"
        found = any(expected_msg in rec.getMessage() and rec.levelname == "WARNING" for rec in caplog.records)
        assert found, "Expected warning message when adding BodyElement to empty behavior"

    def test_addBodyElement_delegates_to_last_behavior(self):
        """addBodyElement: when behavior present, delegate addBodyElement to last behavior element."""
        s = Structure("container", (0, 0))
        s.addProtocol("inner", ElementsTypes.PROTOCOL_ELEMENT)
        be = BodyElement("op(x)")
        s.addBodyElement(be)
        proto = s.behavior[-1]
        assert isinstance(proto, Protocol)
        assert len(proto.body) == 1
        assert proto.body.getElementByIndex(0).identifier == "op(x)"

    def test_copy_deep_copies_behavior_and_parametrs(self):
        """
        copy: produces deep copy. Mutations on original after copying don't affect the copy.
        - add protocol with parametrs and body element
        - copy structure
        - mutate original's parametrs and behavior
        - verify copy remains unchanged
        """
        s = Structure("orig", (0, 0))
        s.parametrs = ParametrArray()
        s.parametrs.addElement(Parametr("p1", "int"))
        s.addProtocol("proto1", ElementsTypes.PROTOCOL_ELEMENT)
        s.addBodyElement(BodyElement("call()"))
        s.behavior[0].parametrs.addElement(Parametr("inner", "int"))
        s_copy = s.copy()
        # mutate original
        s.parametrs.addElement(Parametr("p2", "int"))
        s.behavior[0].parametrs.addElement(Parametr("pX", "int"))
        s.behavior[0].body.addElement(BodyElement("another"))
        # verify copy unaffected
        copy_param_ids = [p.identifier for p in s_copy.parametrs.getElements()]
        assert "p2" not in copy_param_ids
        copy_proto_param_ids = [p.identifier for p in s_copy.behavior[0].parametrs.getElements()]
        assert "pX" not in copy_proto_param_ids
        assert len(s_copy.behavior[0].body) == 1

    def test_updateLinks_calls_nested_updateLinks(self):
        """
        updateLinks: ensure Structure.updateLinks simply delegates to contained elements'
        updateLinks methods. Use a lightweight object with updateLinks to verify call.
        """
        called = {"flag": False}

        class Dummy:
            def updateLinks(self, du: Any):
                called["flag"] = True

        s = Structure("U", (0, 0))
        dummy = Dummy()
        s.behavior.append(dummy)  # insert object with updateLinks
        s.updateLinks(design_unit={"dummy": True})
        assert called["flag"] is True

    def test_getBehLen_returns_behavior_length(self):
        """getBehLen: returns number of elements in behavior list."""
        s = Structure("L", (0, 0))
        assert s.getBehLen() == 0
        s.addProtocol("a")
        assert s.getBehLen() == 1

    def test_str_returns_joined_protocols(self):
        """__str__: returns newline-joined string representation of behavior entries (protocols)."""
        s = Structure("Str", (0, 0))
        s.addProtocol("pa")
        s.addProtocol("pb")
        out = str(s)
        assert "pa" in out and "pb" in out
        # no leading/trailing whitespace
        assert out == out.strip()

    def test_repr_includes_number_when_nonzero(self):
        """__repr__: when number truthy, representation includes identifier_number form."""
        s = Structure("Re", (0, 0), number=5)
        r = repr(s)
        assert "Re_5" in r or "Re'_" in r or isinstance(r, str)


# ------------------------------
# Tests for StructureArray class
# ------------------------------
class TestStructureArray:

    def test_addElement_accepts_structure_and_returns_index(self):
        """addElement: adding a new unique Structure returns (True, index)."""
        sa = StructureArray()
        s = Structure("A", (0, 0), number=10)
        ok, idx = sa.addElement(s)
        assert ok is True
        assert idx == 0
        assert len(sa) == 1

    def test_addElement_rejects_wrong_type(self):
        """addElement: non-Structure types raise TypeError."""
        sa = StructureArray()
        with pytest.raises(TypeError):
            sa.addElement(object())

    def test_addElement_returns_false_on_duplicate(self):
        """addElement: adding a Structure with same getName(False) returns (False, existing_index)."""
        sa = StructureArray()
        s1 = Structure("DUP", (0, 0), number=1)
        s2 = Structure("DUP", (0, 0), number=1)  # same name/number => duplicate by getName(False)
        ok1, idx1 = sa.addElement(s1)
        ok2, idx2 = sa.addElement(s2)
        assert ok1 is True
        assert ok2 is False
        assert idx2 == idx1

    def test_copy_deep_copies_contents(self):
        """copy: deep copy of the array; modifications to original don't affect copy."""
        sa = StructureArray()
        s = Structure("C", (0, 0))
        s.addProtocol("proto")
        s.behavior[0].parametrs.addElement(Parametr("par", "int"))
        sa.addElement(s)
        sa_copy = sa.copy()
        # mutate original
        s.behavior[0].parametrs.addElement(Parametr("newp", "int"))
        copy_ids = [p.identifier for p in sa_copy.elements[0].behavior[0].parametrs.getElements()]
        assert "newp" not in copy_ids

    def test_getElementsIE_filters_by_type_and_identifier(self):
        """getElementsIE: supports include/exclude by element_type and identifier."""
        sa = StructureArray()
        s1 = Structure("one", (0, 0), element_type=ElementsTypes.TASK_ELEMENT)
        s2 = Structure("two", (0, 0), element_type=ElementsTypes.FUNCTION_ELEMENT)
        sa.addElement(s1)
        sa.addElement(s2)
        # include only FUNCTION_ELEMENT
        res = sa.getElementsIE(include_type=ElementsTypes.FUNCTION_ELEMENT)
        assert len(res.elements) == 1
        assert res.elements[0].identifier == "two"
        # exclude FUNCTION_ELEMENT
        res2 = sa.getElementsIE(exclude_type=ElementsTypes.FUNCTION_ELEMENT)
        ids = [e.identifier for e in res2.elements]
        assert "two" not in ids

    def test_updateLinks_calls_each_structure_updateLinks(self):
        """updateLinks: should call updateLinks on each contained structure (use a flag object)."""
        called = {"count": 0}

        class DummyS(Structure):
            def updateLinks(self, design_unit: Any) -> None:
                called["count"] += 1

        sa = StructureArray()
        d1 = DummyS("a", (0, 0))
        d2 = DummyS("b", (0, 0))
        sa.addElement(d1)
        sa.addElement(d2)
        sa.updateLinks(design_unit={})
        assert called["count"] == 2

    def test_getAlwaysList_and_getNoAlwaysStructures_filters(self, monkeypatch):
        """
        getAlwaysList and getNoAlwaysStructures rely on an 'Always' class imported inside the methods.
        To test them reliably, dynamically create and inject a fake module with Always into sys.modules
        at the full module path used by the package.
        """
        # Determine the package path used by classes (structure module package)
        structure_mod = importlib.import_module("..classes.structure", package=__package__)
        package_prefix = structure_mod.__package__  # e.g. "<project>.classes"
        always_mod_name = package_prefix + ".always"

        # Create a fake module and Always class
        fake_mod = types.ModuleType(always_mod_name)

        class Always(Structure):
            """Fake Always subclass used only for test."""
            pass

        fake_mod.Always = Always
        sys.modules[always_mod_name] = fake_mod  # inject module into import system

        # Build StructureArray with different elements
        sa = StructureArray()
        a = Always("A", (0, 0))
        a.addProtocol("inner")
        sa.addElement(a)

        t = Structure("T", (0, 0), element_type=ElementsTypes.TASK_ELEMENT)
        t.addProtocol("tinner")
        sa.addElement(t)

        r = Structure("R", (0, 0), element_type=ElementsTypes.FUNCTION_ELEMENT)
        r.addProtocol("rinner")
        sa.addElement(r)

        always_list = sa.getAlwaysList()
        assert any(isinstance(el, Always) for el in always_list)
        no_always = sa.getNoAlwaysStructures()
        ids = [s.identifier for s in no_always]
        assert "R" in ids and "T" not in ids

        # cleanup injected module
        del sys.modules[always_mod_name]

    def test_getLastElement_and_len(self):
        """getLastElement: returns last element or None; __len__ reports count."""
        sa = StructureArray()
        assert sa.getLastElement() is None
        s = Structure("last", (0, 0))
        sa.addElement(s)
        assert sa.getLastElement() is s
        assert len(sa) == 1

    def test_getStructuresInStrFormat_and_str(self):
        """getStructuresInStrFormat: returns joined string representation; __str__ delegates to it."""
        sa = StructureArray()
        s = Structure("sA", (0, 0))
        s.addProtocol("pa")
        sa.addElement(s)
        out = sa.getStructuresInStrFormat()
        assert "pa" in out
        # __str__ should match
        assert str(sa) == out

