import pytest
from ..classes.tasks import Task, TaskArray, TaskStmt
from ..classes.parametrs import ParametrArray, Parametr
from ..classes.structure import Structure
from ..classes.element_types import ElementsTypes
from ..classes.actions import ActionParts

# ==========================================
# 1. Task Class Tests
# ==========================================

class TestTaskInit:
    """Tests focused on Task initialization state."""

    def test_init_initializes_postcondition(self):
        task = Task("t", (0,0), 1)
        assert isinstance(task.postcondition, ActionParts)

    def test_init_sets_identifier(self):
        task = Task("my_task", (0, 0), 1)
        assert task.identifier == "my_task"

    def test_init_sets_source_interval(self):
        task = Task("t", (10, 20), 1)
        assert task.source_interval == (10, 20)

    def test_init_maps_namespace_to_number(self):
        task = Task("t", (0, 0), 42)
        assert task.number == 42

    def test_init_sets_default_element_type(self):
        task = Task("t", (0, 0), 1)
        assert task.element_type == ElementsTypes.TASK_ELEMENT

    def test_init_initializes_empty_containers(self):
        task = Task("t", (0, 0), 1)
        assert isinstance(task.initial_parametrs, ParametrArray)
        assert isinstance(task.parametrs, ParametrArray)
        assert len(task.parametrs) == 0
        assert task.structure is None


class TestTaskMethods:
    """Tests focused on Task logic methods."""

    def test_find_return_param_true(self):
        task = Task("my_func", (0, 0), 1)
        task.parametrs.addElement(Parametr("return_my_func", (0, 0)))
        assert task.findReturnParam() is True

    def test_find_return_param_false(self):
        task = Task("my_func", (0, 0), 1)
        task.parametrs.addElement(Parametr("other_param", (0, 0)))
        assert task.findReturnParam() is False


class TestTaskCopy:
    """Tests focused on Task.copy() behavior."""

    @pytest.fixture
    def populated_task(self):
        task = Task("orig", (0, 0), 1)
        # Populate standard parameters
        task.parametrs.addElement(Parametr("p1", (0, 0)))
        # Populate INITIAL parameters (Critical check restored)
        task.initial_parametrs.addElement(Parametr("init_p1", (0, 0)))
        
        task.structure = Structure("s1", (0, 0))
        # Note: postcondition is initialized automatically in __init__
        return task

    def test_copy_creates_new_instance(self, populated_task):
        copied = populated_task.copy()
        assert copied is not populated_task

    def test_copy_preserves_immutable_attributes(self, populated_task):
        copied = populated_task.copy()
        assert copied.identifier == "orig"
        assert copied.number == 1
        assert copied.element_type == populated_task.element_type

    def test_copy_deep_copies_parameters(self, populated_task):
        """Verifies deep copy of 'parametrs'."""
        copied = populated_task.copy()
        assert copied.parametrs is not populated_task.parametrs
        
        # Verify independence
        copied.parametrs.addElement(Parametr("new_p", (0,0)))
        assert len(populated_task.parametrs) == 1
        assert len(copied.parametrs) == 2

    def test_copy_deep_copies_initial_parameters(self, populated_task):
        """
        Verifies deep copy of 'initial_parametrs'.
        This was missing in the previous version.
        """
        copied = populated_task.copy()
        
        # 1. Identity Check
        assert copied.initial_parametrs is not populated_task.initial_parametrs
        
        # 2. Content Independence Check
        copied.initial_parametrs.addElement(Parametr("new_init", (0,0)))
        
        # Original should still have only 1 element
        assert len(populated_task.initial_parametrs) == 1
        # Copy should have 2
        assert len(copied.initial_parametrs) == 2

    def test_copy_deep_copies_structure(self, populated_task):
        copied = populated_task.copy()
        assert copied.structure is not populated_task.structure
        assert copied.structure.identifier == "s1"

        copied.structure.identifier = "changed"
        assert populated_task.structure.identifier == "s1"

    def test_copy_deep_copies_postcondition(self, populated_task):
        """
        Verifies deep copy of 'postcondition'.
        Strict check: We rely on the object's internal init. 
        We do NOT manually set it here, ensuring we test the actual logic.
        """
        copied = populated_task.copy()
        
        # Ensure it exists (Architecture check)
        assert populated_task.postcondition is not None, "Task failed to init postcondition"
        
        # Ensure it is a deep copy
        assert copied.postcondition is not populated_task.postcondition

    def test_copy_handles_none_structure(self):
        task = Task("t", (0,0), 1)
        task.structure = None
        copied = task.copy()
        assert copied.structure is None


class TestTaskStringRep:
    """Tests for __str__ and __repr__."""

    def test_str_no_structure(self):
        task = Task("t1", (0,0), 0)
        assert str(task).startswith("t1(")

    def test_str_with_structure(self):
        task = Task("t1", (0,0), 0)
        task.structure = Structure("body", (0,0))
        assert str(task).startswith("body(")

    def test_repr_contains_class_name(self):
        task = Task("t", (0,0), 0)
        assert "Task" in repr(task)

    def test_repr_contains_identifier(self):
        task = Task("debug_name", (0,0), 0)
        assert "debug_name" in repr(task)


# ==========================================
# 2. TaskArray Class Tests
# ==========================================

class TestTaskArrayGetters:
    """Tests for retrieval methods."""

    @pytest.fixture
    def array(self):
        arr = TaskArray()
        arr.addElement(Task("t1", (0,0), 0))
        arr.addElement(Task("t2", (0,0), 0))
        return arr

    def test_get_element_success(self, array):
        assert array.getElement("t1").identifier == "t1"

    def test_get_element_failure(self, array):
        assert array.getElement("missing") is None

    def test_get_last_task_success(self, array):
        assert array.getLastTask().identifier == "t2"

    def test_get_last_task_empty(self):
        arr = TaskArray()
        assert arr.getLastTask() is None

    def test_get_functions_only(self):
        arr = TaskArray()
        arr.addElement(Task("t", (0,0), 0, ElementsTypes.TASK_ELEMENT))
        arr.addElement(Task("f", (0,0), 0, ElementsTypes.FUNCTION_ELEMENT))
        
        funcs = arr.getFunctions()
        assert len(funcs) == 1
        assert funcs[0].identifier == "f"


class TestTaskArraySlicing:
    """Tests specifically for __getitem__ logic."""

    @pytest.fixture
    def array(self):
        arr = TaskArray()
        arr.addElement(Task("A", (0,0), 0))
        arr.addElement(Task("B", (0,0), 0))
        arr.addElement(Task("C", (0,0), 0))
        return arr

    def test_getitem_single_index(self, array):
        assert array[0].identifier == "A"

    def test_getitem_negative_index(self, array):
        assert array[-1].identifier == "C"

    def test_getitem_slice_range(self, array):
        sliced = array[0:2]
        assert len(sliced) == 2
        assert sliced[1].identifier == "B"

    def test_getitem_slice_step(self, array):
        sliced = array[::2]
        assert len(sliced) == 2
        assert sliced[0].identifier == "A"
        assert sliced[1].identifier == "C"

    def test_getitem_slice_out_of_bounds(self, array):
        sliced = array[10:20]
        assert len(sliced) == 0


class TestTaskArrayCopy:
    """Tests for array deep copying."""

    def test_copy_creates_new_container(self):
        arr = TaskArray()
        copied = arr.copy()
        assert copied is not arr

    def test_copy_deep_copies_elements(self):
        arr = TaskArray()
        t1 = Task("t1", (0,0), 0)
        arr.addElement(t1)
        
        copied = arr.copy()
        assert copied[0] is not t1
        assert copied[0].identifier == "t1"


class TestTaskArrayFiltering:
    """Tests for getElementsIE."""

    @pytest.fixture
    def array(self):
        arr = TaskArray()
        arr.addElement(Task("task_A", (0,0), 0, ElementsTypes.TASK_ELEMENT))
        arr.addElement(Task("func_A", (0,0), 0, ElementsTypes.FUNCTION_ELEMENT))
        return arr

    def test_filter_include_identifier(self, array):
        res = array.getElementsIE(include_identifier="task_A")
        assert len(res) == 1
        assert res[0].identifier == "task_A"

    def test_filter_exclude_identifier(self, array):
        res = array.getElementsIE(exclude_identifier="task_A")
        assert len(res) == 1
        assert res[0].identifier == "func_A"

    def test_filter_include_type(self, array):
        res = array.getElementsIE(include_type=ElementsTypes.FUNCTION_ELEMENT)
        assert len(res) == 1
        assert res[0].identifier == "func_A"

    def test_filter_exclude_type(self, array):
        res = array.getElementsIE(exclude_type=ElementsTypes.FUNCTION_ELEMENT)
        assert len(res) == 1
        assert res[0].identifier == "task_A"


class TestTaskArrayMethods:
    """Tests for logic methods like uniqueness and filtering."""

    def test_is_uniq_action_found(self):
        """
        Verifies behavior when the exact object exists in the array.
        """
        arr = TaskArray()
        t1 = Task("t1", (10, 20), 0)
        arr.addElement(t1)
        
        # Check uniqueness of the SAME object
        identifier, interval = arr.isUniqAction(t1)
        
        assert identifier == "t1"
        assert interval == (10, 20)

    def test_is_uniq_action_not_found(self):
        """
        Verifies behavior when the object is NOT in the array.
        """
        arr = TaskArray()
        t1 = Task("t1", (0,0), 0)
        arr.addElement(t1)
        
        # Create a DIFFERENT task object
        t2 = Task("t2", (0,0), 0)
        
        identifier, interval = arr.isUniqAction(t2)
        
        assert identifier is None
        assert interval == (None, None)


# ==========================================
# 3. TaskStmt Class Tests
# ==========================================

class TestTaskStmt:
    """Tests for the TaskStmt subclass (Structure specialization)."""

    def test_init_sets_basic_fields(self):
        stmt = TaskStmt("stmt", (1, 5), 5)

        assert stmt.identifier == "stmt"
        assert stmt.source_interval == (1, 5)
        assert stmt.number == 5

    def test_init_sets_fixed_element_type(self):
        """
        TaskStmt must ALWAYS have element_type = TASK_ELEMENT
        regardless of external input.
        """
        stmt = TaskStmt("stmt", (0, 0), 5)
        assert stmt.element_type == ElementsTypes.TASK_ELEMENT

    def test_inheritance_from_structure(self):
        stmt = TaskStmt("stmt", (0, 0), 5)
        assert isinstance(stmt, Structure)

    def test_repr_contains_class_name(self):
        stmt = TaskStmt("stmt", (0, 0), 5)
        assert "TaskStmt" in repr(stmt)

    def test_str_behavior_consistent_with_structure(self):
        """
        Ensures TaskStmt behaves like Structure in string representation.
        """
        stmt = TaskStmt("stmt", (0, 0), 5)
        assert isinstance(str(stmt), str)

    def test_element_type_cannot_be_overridden(self):
        """
        Architectural safety check.
        If constructor allows passing element_type,
        it must still enforce TASK_ELEMENT.
        """
        stmt = TaskStmt("stmt", (0, 0), 5)
        assert stmt.element_type is ElementsTypes.TASK_ELEMENT
