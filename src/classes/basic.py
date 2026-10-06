import copy
from typing import Any, List, Tuple, Type
from ..classes.element_types import ElementsTypes
from ..utils.counters import Counters
from ..logger.logger import Logger, LoggerManager
from ..utils.string_formater import StringFormater
from ..utils.unsorted import UnsortedUnils


class Basic:
    """
    Base class for language elements.
    It holds common attributes like an identifier, source code interval,
    element type, and a sequence number.
    """

    # Class-level attributes for shared utilities.
    # These are assumed to be singletons or stateless helpers
    # that all instances of Basic (and its subclasses) can share.
    counters = Counters()
    utils = UnsortedUnils()
    string_formater = StringFormater()

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int] = (0, 0),
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
    ):
        """
        Initializes a new Basic object.

        Args:
            identifier (str): The unique name or identifier of the element.
            source_interval (Tuple[int, int]): A tuple representing the start and end
                                               positions of the element in the source code.
            element_type (ElementsTypes): The type of the element, defaulting to NONE_ELEMENT.
        """
        self.identifier: str = identifier
        # Assigns a unique sequence number from the global counter.
        # Changed from a tuple to an int, assuming sequence is always a single number.
        self.sequence: int = self.counters.get(self.counters.types.SEQUENCE_COUNTER)
        self.source_interval: Tuple[int, int] = source_interval
        self.element_type: ElementsTypes = element_type
        self.number: int | None = (
            None  # Optional numerical suffix, e.g., for unique naming in context.
        )
        self.logger: Logger = LoggerManager().getLogger(self.__class__.__qualname__)

    def copy(self) -> "Basic":
        """
        Creates a shallow copy of the Basic object.
        For this class, as it primarily contains immutable types (str, int, tuple, enum),
        a shallow copy effectively behaves like a deep copy for its own attributes.

        Returns:
            Basic: A new Basic object with identical attribute values.
        """
        new_basic = Basic(
            self.identifier,
            self.source_interval,
            self.element_type,
        )
        # Explicitly copy `sequence` and `number` as they are not passed to __init__
        # but are part of the object's state.
        new_basic.sequence = self.sequence
        new_basic.number = self.number
        return new_basic

    def __deepcopy__(self, memo: dict[int, Any]) -> "Basic":
        """
        Implements the deep copy protocol.
        Delegates to the custom `copy` method, as it's sufficient for this class's attributes.
        `memo` is used to prevent infinite recursion for circular references.

        Args:
            memo (dict): A dictionary used by the deepcopy mechanism to store already copied objects.

        Returns:
            Basic: A new Basic object representing a deep copy.
        """
        new_basic = self.copy()
        memo[id(self)] = (
            new_basic  # Store the new object in memo to handle circular references
        )
        return new_basic

    def getName(self) -> str:
        """
        Returns the name of the element.
        If a `number` is assigned, the name will be formatted as "identifier_number".

        Returns:
            str: The element's name.
        """
        # Uses an f-string for concise and readable string formatting.
        return (
            self.identifier
            if self.number is None
            else f"{self.identifier}_{self.number}"
        )

    def __repr__(self) -> str:
        """
        Returns a string representation of the Basic object for debugging purposes.
        Includes all key attributes for comprehensive information.

        Returns:
            str: A formatted string representation of the object.
        """
        # Uses f-strings for clear representation. `!r` ensures the value's repr is used.
        # `.name` is used for `ElementsTypes` enum to show its string name.
        # The leading tab `\t` has been removed for cleaner output.
        return (
            f"Basic(identifier={self.identifier!r}, sequence={self.sequence!r}, "
            f"source_interval={self.source_interval!r}, element_type={self.element_type.name!r}, "
            f"number={self.number!r})"
        )


class BasicArray:
    """
    A dynamic array class designed to hold objects of type 'Basic' or its subclasses.
    Provides methods for common array operations like adding, removing, accessing,
    and filtering elements.
    """

    # Class-level instances for utility functions and logging.
    # These are initialized once and shared across all BasicArray instances.
    counters = Counters()
    utils = UnsortedUnils()
    string_formater = StringFormater()

    def __init__(self, element_type: Type[Basic] = Basic):
        """
        Initializes a new BasicArray instance.

        Args:
            element_type (Type[Basic]): The expected type of elements this array will hold.
                                        Defaults to Basic.
        """
        self.elements = []
        self.element_type: Type[Basic] = element_type
        self.logger: Logger = LoggerManager().getLogger(self.__class__.__qualname__)

    def __len__(self) -> int:
        """
        Returns the number of elements in the array.
        Allows the use of len() on a BasicArray instance.
        """
        return len(self.elements)

    def __iter__(self):
        """
        Returns an iterator over the elements in the array.
        Allows iteration (e.g., in a for loop) over a BasicArray instance.
        """
        return iter(self.elements)

    def __getitem__(self, index: int) -> Basic:
        """
        Allows accessing elements by index using bracket notation (e.g., array[0]).

        Args:
            index (int): The index of the element to retrieve.

        Returns:
            Basic: The element at the specified index.
        """
        return self.elements[index]

    def addElement(self, new_element: Basic) -> int:
        """
        Adds a new element to the end of the array.
        Performs a type check to ensure the element matches the expected `element_type`.

        Args:
            new_element (Basic): The element to add.

        Returns:
            int: The index of the newly added element.
        """
        if not isinstance(new_element, self.element_type):
            self.logger.warning(
                f"Object should be of type {self.element_type.__name__} but received "
                f"an object of type {type(new_element).__name__}. Object: {new_element}"
            )
        self.elements.append(new_element)
        return len(self.elements) - 1

    def checkSourceInteval(self, source_interval: Tuple[int, int]) -> bool:
        """
        Checks if the given `source_interval` is contained within the `source_interval`
        of any existing element in the array.

        Args:
            source_interval (Tuple[int, int]): The interval to check.

        Returns:
            bool: False if the `source_interval` is contained within any element's
                  source interval, True otherwise.
        """
        for element in self.elements:
            if self.utils.is_interval_contained(
                source_interval, element.source_interval
            ):
                return False
        return True

    def copy(self) -> "BasicArray":
        """
        Creates a shallow copy of the BasicArray.
        Elements themselves are shallow copied (their 'copy' method is called).

        Returns:
            BasicArray: A new BasicArray instance containing copies of the original elements.
        """
        new_array = BasicArray(self.element_type)
        for element in self.elements:
            new_array.addElement(element.copy())  # Calls the element's copy method
        return new_array

    def __deepcopy__(self, memo: dict[int, Any]) -> "BasicArray":
        """
        Implementation of the deep copy method.
        This allows for a truly independent copy where all nested objects are also copied.

        Args:
            memo (dict): A dictionary used internally by `copy.deepcopy` to keep track of
                         objects already copied during the current deep copy operation,
                         preventing infinite recursion for self-referencing objects.

        Returns:
            BasicArray: A new BasicArray instance with deep copies of all its elements.
        """
        new_array = BasicArray(self.element_type)
        memo[id(self)] = new_array  # Register the new array in the memo
        for element in self.elements:
            new_array.addElement(copy.deepcopy(element, memo))
        return new_array

    def reverse(self) -> "BasicArray":
        """
        Reverses the order of elements in the array in-place.

        Returns:
            BasicArray: The current BasicArray instance with elements reversed.
        """
        self.elements.reverse()
        return self

    def reverse_copy(self) -> "BasicArray":
        """
        Creates a new BasicArray with the elements in reversed order,
        leaving the original array unchanged.

        Returns:
            BasicArray: A new BasicArray instance with elements in reverse order.
        """
        new_array = self.copy()  # Create a shallow copy first
        new_array.elements.reverse()  # Reverse the elements of the new copy
        return new_array

    def insert(self, index: int, element: Basic):
        """
        Inserts an element at a specified index in the array.

        Args:
            index (int): The index at which to insert the element.
            element (Basic): The element to insert.
        """
        self.elements.insert(index, element)

    def getElementsIE(
        self,
        include: ElementsTypes | None = None,
        exclude: ElementsTypes | None = None,
        include_identifier: str | None = None,
        exclude_identifier: str | None = None,
    ) -> "BasicArray":
        """
        Filters the elements of the array based on type and identifier criteria.

        Args:
            include (ElementsTypes | None): If provided, only elements with this
                                            `element_type` will be included.
            exclude (ElementsTypes | None): If provided, elements with this
                                            `element_type` will be excluded.
            include_identifier (str | None): If provided, only elements with this
                                             `identifier` will be included.
            exclude_identifier (str | None): If provided, elements with this
                                             `identifier` will be excluded.

        Returns:
            BasicArray: A new BasicArray containing the filtered elements.
                        Returns a deep copy of the current array if no filters are applied.
        """
        # If no filters are provided, return a deep copy of the current array
        if not any([include, exclude, include_identifier, exclude_identifier]):
            return self.copy()

        result_array: BasicArray = BasicArray(self.element_type)
        for element in self.elements:
            # Use 'is not None' for checking against None
            if include is not None and element.element_type is not include:
                continue
            if exclude is not None and element.element_type is exclude:
                continue
            # Use '!=' or '==' for string comparison, not 'is'
            if (
                include_identifier is not None
                and element.identifier != include_identifier
            ):
                continue
            if (
                exclude_identifier is not None
                and element.identifier == exclude_identifier
            ):
                continue

            result_array.addElement(element)
        return result_array

    def __iadd__(self, other: "BasicArray | Basic") -> "BasicArray":
        """
        Implements the in-place addition operator (+=).
        Allows adding another BasicArray or a single Basic element to the current array.

        Args:
            other (BasicArray | Basic): The object to add. Can be another BasicArray
                                        or a single Basic element.

        Returns:
            BasicArray: The modified BasicArray instance.

        Raises:
            TypeError: If the 'other' object is not of type Basic or BasicArray.
        """
        if isinstance(other, BasicArray):
            if self.element_type != other.element_type:
                self.logger.warning(
                    f"Adding BasicArray of type {other.element_type.__name__} to "
                    f"BasicArray of type {self.element_type.__name__}. Potential type mismatch."
                )
            self.elements.extend(other.elements)
        elif isinstance(other, Basic):
            self.addElement(other)
        else:
            raise TypeError(
                f"Cannot add object of type {type(other).__name__} to BasicArray. "
                f"Expected Basic or BasicArray."
            )
        return self

    def getElement(self, identifier: str) -> Basic | None:
        """
        Retrieves an element by its identifier.

        Args:
            identifier (str): The unique identifier of the element to retrieve.

        Returns:
            Basic | None: The element if found, otherwise None.
        """
        for element in self.elements:
            if element.identifier == identifier:
                return element
        return None

    def getElementIndex(self, identifier: str) -> int | None:
        """
        Retrieves the index of an element by its identifier.

        Args:
            identifier (str): The unique identifier of the element.

        Returns:
            int | None: The index of the element if found, otherwise None.
        """
        for index, element in enumerate(self.elements):
            if element.identifier == identifier:
                return index
        return None

    def getElementByIndex(self, index: int) -> Basic:
        """
        Retrieves an element by its numerical index.

        Args:
            index (int): The index of the element to retrieve.

        Returns:
            Basic: The element at the specified index.
        """
        return self.elements[index]

    def getLastElement(self) -> Basic | None:
        """
        Retrieves the last element in the array.

        Returns:
            Basic | None: The last element if the array is not empty, otherwise None.
        """
        return self.elements[-1] if self.elements else None

    def removeElement(self, element: Basic):
        """
        Removes a specific element from the array.

        Args:
            element (Basic): The element to remove.
        """
        self.elements.remove(element)

    def removeElementByIndex(self, index: int):
        """
        Removes an element at a specific index from the array.

        Args:
            index (int): The index of the element to remove.
        """
        if 0 <= index < len(self.elements):
            del self.elements[index]

    def getElements(self) -> List[Basic]:
        """
        Returns all elements currently in the array.

        Returns:
            List[Basic]: A list containing all elements.
        """
        return self.elements

    def __repr__(self) -> str:
        """
        Provides a string representation of the BasicArray object,
        useful for debugging and logging.
        """
        elements_repr = ",\n".join([repr(e).strip() for e in self.elements])
        return (
            f"BasicArray(element_type={self.element_type.__name__}, count={len(self.elements)}):\n"
            f"[\n{elements_repr}\n]"
        )

    def addElements(self, new_elements: "BasicArray") -> int:
        """
        Adds multiple elements from another BasicArray to this array.

        Args:
            new_elements (BasicArray): The BasicArray containing elements to add.

        Returns:
            int: The index of the last added element.
        """
        last_index = -1
        for element in new_elements.elements:
            last_index = self.addElement(element)
        return last_index
