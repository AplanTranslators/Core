import re
from typing import Optional, Tuple, List
from enum import Enum, auto

from ..logger.logger import AplanLogger
from ..classes.actions import Action
from ..classes.basic import Basic, BasicArray
from ..classes.element_types import ElementsTypes


class DeclTypes(Enum):
    """
    An enumeration representing various data types and declaration types commonly
    found in hardware description languages (HDL) like SystemVerilog, or similar
    structured programming contexts.

    Each member of this enum corresponds to a specific type of declaration
    (e.g., 'wire', 'reg', 'int', 'logic', or complex types like 'struct', 'class').
    """

    # Basic data types
    WIRE = auto()  # Represents a 'wire' declaration (e.g., in Verilog)
    INT = auto()  # Represents an 'int' (integer) declaration
    REG = auto()  # Represents a 'reg' (register) declaration
    LOGIC = auto()  # Represents a 'logic' declaration (SystemVerilog)
    STRING = auto()  # Represents a 'string' type
    BIT = auto()  # Represents a 'bit' type
    TIME = auto()  # Represents a 'time' type
    REAL = auto()  # Represents a 'real' (floating-point) type
    ARRAY = auto()  # Represents an array type

    # Port types
    INPORT = auto()  # Represents an input port declaration
    OUTPORT = auto()  # Represents an output port declaration

    # User-defined or complex types
    ENUM = auto()  # Represents an instance of an enumerated type
    ENUM_TYPE = auto()  # Represents the definition of an enumerated type
    STRUCT = auto()  # Represents an instance of a structured type
    STRUCT_TYPE = auto()  # Represents the definition of a structured type
    UNION = auto()  # Represents an instance of a union type
    UNION_TYPE = auto()  # Represents the definition of a union type
    CLASS = auto()  # Represents a class type (e.g., SystemVerilog class)

    # Default/None type
    NONE = auto()  # Represents an undefined or unhandled type

    @staticmethod
    def checkType(type_str: str, types) -> "DeclTypes":
        """
        Determines the `DeclTypes` enum member corresponding to a given
        type string.

        This method first checks for primitive/built-in types (e.g., "int", "wire").
        If not found, it then iterates through a collection of custom/user-defined
        types (`types` argument) to find a match.

        Args:
            type_str (str): The string representation of the type to check (e.g., "logic", "my_module").
            types (Iterable[Union[DesignUnit, DeclTypeInfo]]): An iterable collection of
                known type definitions. This could include `DesignUnit` objects (for class-like
                design_units) or other custom type definition objects (e.g., an object
                that holds `identifier` and `data_type` attributes for enums/structs/unions).

        Returns:
            DeclTypes: The corresponding `DeclTypes` enum member, or `DeclTypes.NONE`
                       if no matching type is found.
        """
        # Defer import here to prevent potential circular dependency issues,
        # especially if DesignUnit also needs to import DeclTypes.
        from .design_unit import DesignUnit

        # Standard built-in types check
        if type_str == "int":
            return DeclTypes.INT
        elif type_str == "real":
            return DeclTypes.REAL
        elif type_str == "time":
            return DeclTypes.TIME
        elif type_str == "reg":
            return DeclTypes.REG
        elif type_str == "logic" or type_str == "std_logic":
            return DeclTypes.LOGIC
        elif type_str == "wire":
            return DeclTypes.WIRE
        elif type_str == "string":
            return DeclTypes.STRING
        elif type_str == "bit":
            return DeclTypes.BIT
        # Add checks for ARRAY, INPORT, OUTPORT if they are parsed as simple strings
        # elif type_str == "array":
        #     return DeclTypes.ARRAY
        # elif type_str == "input":
        #     return DeclTypes.INPORT
        # elif type_str == "output":
        #     return DeclTypes.OUTPORT

        # Custom/user-defined types check
        # This assumes that `types` contains objects that are either `DesignUnit` instances
        # or objects with `identifier` and `data_type` attributes.
        for known_type_definition in types:
            if isinstance(known_type_definition, DesignUnit):
                # If it's a DesignUnit, compare with its unique identifier (e.g., design_unit name)
                if type_str == known_type_definition.ident_uniq_name:
                    return (
                        DeclTypes.CLASS
                    )  # Treating design_units as 'classes' in this context
            else:
                # For other custom types, assume they have 'identifier' and 'data_type' attributes
                # Example: an object representing an enum, struct, or union definition.
                # It's good practice to ensure these attributes exist, e.g., using hasattr().
                if hasattr(known_type_definition, "identifier") and hasattr(
                    known_type_definition, "data_type"
                ):
                    if type_str == known_type_definition.identifier:
                        if known_type_definition.data_type is DeclTypes.ENUM_TYPE:
                            return DeclTypes.ENUM
                        elif known_type_definition.data_type is DeclTypes.STRUCT_TYPE:
                            return DeclTypes.STRUCT
                        elif known_type_definition.data_type is DeclTypes.UNION_TYPE:
                            return DeclTypes.UNION

        # If no match is found, return NONE
        return DeclTypes.NONE


class AplanDeclType(Enum):
    """
    An enumeration representing high-level declaration types relevant to
    an 'Aplan' context. This likely categorizes how certain declarations
    are handled or interpreted within a specific planning or analysis system.
    """

    STRUCT = auto()  # Indicates a structure declaration.
    PARAMETRS = auto()  # Indicates a parameter or a group of parameters.
    NONE = auto()  # Represents an undefined or unclassified type.


class DeclType:
    """
    Represents the detailed information about a declared type in a system.
    This class holds properties such as the fundamental data type, its size,
    and its hierarchical context within the code.
    """

    def __init__(
        self,
        data_type: DeclTypes,
        size_expression: str,
        size: int,
        name_space_level: int,
        inside_the_struct: bool = False,
    ):
        """
        Initializes a new DeclType instance.

        Args:
            data_type (DeclTypes): The fundamental type of the declaration
                                   (e.g., WIRE, INT, LOGIC, STRUCT).
            size_expression (str): A string representation of the size expression
                                   for the declaration (e.g., "[7:0]", "[WIDTH-1:0]").
                                   This is useful for retaining the original text.
            size (int): The calculated numerical size of the declaration.
                        For a single bit, this might be 1; for a 8-bit wire, 8.
            name_space_level (int): The hierarchical nesting level where this
                                    declaration is defined. A higher number
                                    indicates deeper nesting.
            inside_the_struct (bool, optional): A flag indicating if this
                                                declaration is part of a structure.
                                                Defaults to False.
        """
        self.data_type: DeclTypes = data_type
        self.size_expression: str = size_expression
        self.size: int = size
        self.name_space_level: int = name_space_level
        self.inside_the_struct: bool = inside_the_struct

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the DeclType object.
        This provides a clear and concise view of the object's state,
        useful for debugging and logging.
        """
        return (
            f"DeclType(data_type={self.data_type!r}, "
            f"size_expression={self.size_expression!r}, "
            f"size={self.size!r}, "
            f"name_space_level={self.name_space_level!r}, "
            f"inside_the_struct={self.inside_the_struct!r})"
        )

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the DeclType object.
        This formats the type and its size for display purposes.
        """
        if self.size_expression:
            return f"{self.data_type.name} {self.size_expression}"
        return self.data_type.name

    def __eq__(self, other: object) -> bool:
        """
        Compares this DeclType object to another for equality.
        Two DeclType objects are considered equal if all their key attributes
        (data_type, size_expression, size, name_space_level, inside_the_struct) match.
        """
        if not isinstance(other, DeclType):
            return NotImplemented
        return (
            self.data_type == other.data_type
            and self.size_expression == other.size_expression
            and self.size == other.size
            and self.name_space_level == other.name_space_level
            and self.inside_the_struct == other.inside_the_struct
        )

    def __hash__(self) -> int:
        """
        Returns the hash value for the DeclType object.
        This is necessary to use DeclType objects in sets or as dictionary keys.
        The hash is based on the same attributes used for equality comparison.
        """
        return hash(
            (
                self.data_type,
                self.size_expression,
                self.size,
                self.name_space_level,
                self.inside_the_struct,
            )
        )


class DeclTypeArray:
    """
    A specialized collection class for managing an array of `DeclType` objects.

    This class provides fundamental operations for handling a list of type
    declarations, including adding, retrieving, and managing the elements
    in a structured way.
    """

    def __init__(self):
        """
        Initializes a new `DeclTypeArray` instance with an empty list
        to store `DeclType` objects.
        """
        self.elements: List[DeclType] = []

    def getElements(self) -> List[DeclType]:
        """
        Retrieves the underlying list of `DeclType` elements.

        Returns:
            List[DeclType]: A list containing all `DeclType` objects currently
                            stored in the array.
        """
        return self.elements

    def addElement(self, new_element: DeclType):
        """
        Adds a new `DeclType` object to the end of the array.

        Args:
            new_element (DeclType): The `DeclType` object to be added.
        """
        self.elements.append(new_element)

    def __len__(self) -> int:
        """
        Returns the number of `DeclType` objects currently in the array.
        This allows `len()` to be used directly on `DeclTypeArray` instances.

        Returns:
            int: The total count of elements.
        """
        return len(self.elements)

    def getLastElement(self) -> Optional[DeclType]:
        """
        Retrieves the last `DeclType` object added to the array.

        Returns:
            Optional[DeclType]: The last `DeclType` object if the array is not empty,
                                otherwise `None`.
        """
        if self.elements:  # More Pythonic way to check if list is not empty
            return self.elements[-1]  # Access the last element directly
        return None

    def removeLastElement(self):
        """
        Removes the last `DeclType` object from the array if it exists.
        If the array is empty, this method does nothing.
        """
        if self.elements:  # Check if there are elements to remove
            self.elements.pop()  # Use pop() for efficient removal of the last element

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the `DeclTypeArray`.
        It lists all elements, each on a new line.
        """
        return "\n".join(str(element) for element in self.elements)

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `DeclTypeArray` object.
        This includes the class name and the `repr` of its internal list of elements,
        useful for debugging.
        """
        return f"DeclTypeArray(elements={self.elements!r})"

    def __iter__(self):
        """
        Makes the `DeclTypeArray` iterable, allowing direct iteration over its elements
        (e.g., `for decl_type in my_decl_array:`).
        """
        return iter(self.elements)


class Declaration(Basic):
    """
    Represents a single variable or type declaration within a hardware description
    language (HDL) context, such as SystemVerilog.

    This class extends `Basic`, inheriting core properties like an identifier
    and source code interval. It encapsulates detailed information about a
    declaration, including its type, size, dimensions, and associated actions.
    """

    def __init__(
        self,
        data_type: DeclTypes,
        identifier: str,
        expression: str = "",
        size_expression: str = "",
        size: int = 0,
        dimension_expression: str = "",
        dimension_size: int = 0,
        source_interval: Tuple[int, int] = (0, 0),
        element_type: ElementsTypes = ElementsTypes.NONE_ELEMENT,
        action: Optional[Action] = None,
        struct_name: Optional[str] = None,
        name_space_level: Optional[int] = None,
    ):
        """
        Initializes a new Declaration instance.

        Args:
            data_type (DeclTypes): The fundamental type of the declared entity
                                   (e.g., DeclTypes.WIRE, DeclTypes.INT, DeclTypes.STRUCT).
            identifier (str): The unique name or identifier of the declared entity.
            expression (str): The original string expression used in the declaration.
                              This might include assignment values or complex initializations.
            size_expression (str): The string representing the bit-width or size expression
                                   (e.g., "[7:0]", "[WIDTH-1:0]").
            size (int): The calculated numerical size (bit-width) of the declaration.
                        For a single bit, this is 1; for an 8-bit wire, 8.
            dimension_expression (str): The string representing array dimensions (e.g., "[0:N-1]").
            dimension_size (int): The calculated numerical size of the array dimension.
                                  For a scalar, this would be 0 or 1.
            source_interval (Tuple[int, int]): A tuple (start_position, end_position)
                                                indicating where this declaration
                                                appears in the original source file.
            element_type (ElementsTypes, optional): The classification of this declaration
                                                    as an element type. Defaults to NONE_ELEMENT.
            action (Optional[Action], optional): An associated action object, if this
                                                 declaration triggers or is part of an action.
                                                 Defaults to None.
            struct_name (Optional[str], optional): The name of the structure if this
                                                   declaration is part of a struct instance.
                                                   Defaults to None.
            name_space_level (Optional[int], optional): The hierarchical nesting level
                                                         of this declaration within the code's
                                                         namespace. This is mapped to `self.number`.
                                                         Defaults to None.
        """
        # Initialize properties from the parent `Basic` class.
        super().__init__(identifier, source_interval, element_type)

        # Assign namespace level to 'number', an attribute inherited from Basic.
        # This reuses 'number' to represent the hierarchical level.
        self.number: Optional[int] = name_space_level

        # Core declaration properties
        self.data_type: DeclTypes = data_type
        self.expression: str = expression
        self.size: int = size
        self.size_expression: str = size_expression
        self.dimension_expression: str = dimension_expression
        self.dimension_size: int = dimension_size

        # Optional associated objects/metadata
        self.action: Optional[Action] = action
        self.file_path: str = ""  # Path to the source file where declared
        self.struct_name: Optional[str] = (
            struct_name  # Name of the parent struct if applicable
        )

    def copy(self) -> "Declaration":
        """
        Creates a deep copy of the current `Declaration` instance.
        This ensures that when a `Declaration` object is copied, all its mutable
        attributes (like `Action` if it's mutable) are also independently copied,
        preventing unintended side effects from modifications to the copy.

        Returns:
            Declaration: A new `Declaration` object that is a deep copy of the original.
        """
        # Create a new Declaration instance, passing all current attribute values.
        # For immutable types (str, int, enum), direct assignment is effectively a deep copy.
        # For the 'action' attribute, if it's an object, its .copy() method is called
        # to ensure a deep copy of the associated action.
        copied_action = self.action.copy() if self.action else None

        declaration_copy = Declaration(
            data_type=self.data_type,
            identifier=self.identifier,
            expression=self.expression,
            size_expression=self.size_expression,
            size=self.size,
            dimension_expression=self.dimension_expression,
            dimension_size=self.dimension_size,
            source_interval=self.source_interval,
            element_type=self.element_type,
            action=copied_action,  # Pass the copied action
            struct_name=self.struct_name,
            name_space_level=self.number,  # Use self.number which holds the namespace level
        )
        # Copy file_path as it's a simple string.
        declaration_copy.file_path = self.file_path
        return declaration_copy

    def getAplanDecltype(self, aplan_type: AplanDeclType = AplanDeclType.NONE) -> str:
        """
        Generates a string representation of the declaration type,
        formatted for an "Aplan" specific output or analysis context.

        The output format varies based on the `DeclTypes` and whether it's
        part of a struct or a parameter context.

        Args:
            aplan_type (AplanDeclType, optional): Specifies the context for
                                                  formatting (e.g., STRUCT, PARAMETRS).
                                                  Defaults to AplanDeclType.NONE.

        Returns:
            str: A formatted string representing the Aplan declaration type.
        """
        result = ""

        # Prepend identifier if this is a struct member context
        if aplan_type is AplanDeclType.STRUCT:
            result += f"{self.identifier}:"

        # Determine the Aplan type string based on `data_type` and other properties
        if self.data_type == DeclTypes.INT:
            if self.dimension_size > 0:
                result += "(int) -> int"  # Example: array of ints
            else:
                result += "int"
        elif self.data_type == DeclTypes.REAL:
            if self.dimension_size > 0:
                result += "(float) -> float"  # Example: array of floats
            else:
                result += "float"
        elif self.data_type == DeclTypes.ARRAY:
            # For a generic array, use its size expression
            result += f"{self.size_expression}"
        elif (
            self.data_type == DeclTypes.INPORT
            or self.data_type == DeclTypes.OUTPORT
            or self.data_type == DeclTypes.WIRE
            or self.data_type == DeclTypes.REG
            or self.data_type == DeclTypes.LOGIC
            or self.data_type == DeclTypes.BIT  # Added BIT for explicit handling
        ):
            if self.dimension_size > 0:
                # If it's a multi-dimensional bit type (e.g., array of vectors)
                if aplan_type is AplanDeclType.PARAMETRS:
                    # Specific format for parameters: "Bits [total size]"
                    result += f"Bits {self.size}"
                else:
                    # General array of bit types: "(Bits [element size]) -> Bits [dimension size]"
                    result += f"(Bits {self.size}) -> Bits {self.dimension_size}"
            elif self.size > 0:
                # If it's a single-dimension bit vector (size > 0, dimension_size == 0)
                result += f"Bits {self.size}"
            else:
                # If it's a single bit (size 0 or 1, no dimension)
                result += "bool"  # Represents a single bit as a boolean
        elif self.data_type == DeclTypes.ENUM_TYPE:
            # Enum type definitions might not have a direct Aplan representation here
            result += ""  # Or a specific Aplan equivalent if applicable
        elif self.data_type == DeclTypes.CLASS:
            # For class types, use the size expression (likely the class name itself)
            result += f"{self.size_expression}"
        elif self.data_type == DeclTypes.STRING:
            result += "string"
        elif (
            self.data_type == DeclTypes.ENUM
            or self.data_type == DeclTypes.STRUCT
            or self.data_type == DeclTypes.UNION
        ):
            # For instances of user-defined types, use their size expression (likely their type name)
            result += f"{self.size_expression}"
        elif self.data_type == DeclTypes.TIME:
            result += "Bits 64"  # Time is often represented as 64-bit integer

        # If DeclTypes.NONE or other unhandled types, result will remain empty
        return result

    def logAgentsTypes2Aplan(self, logger: AplanLogger):
        logger.envPush("\t\t\t{0}:{1}".format(self.getName(), self.getAplanDecltype()))

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the Declaration object.
        This provides a common way to display the declaration,
        e.g., "logic [31:0] my_var".
        """
        type_str = self.data_type.name.lower()  # Convert enum name to lowercase string

        # Handle specific cases for presentation
        if self.data_type in (DeclTypes.INPORT, DeclTypes.OUTPORT):
            # For ports, show as "input" or "output"
            type_str = "input" if self.data_type == DeclTypes.INPORT else "output"
        elif self.data_type in (
            DeclTypes.ENUM_TYPE,
            DeclTypes.STRUCT_TYPE,
            DeclTypes.UNION_TYPE,
        ):
            # These are type definitions, not instances of types;
            # their string representation might just be their identifier.
            return self.identifier

        size_dim_str = ""
        if self.size_expression:
            size_dim_str += self.size_expression
        if self.dimension_expression:
            # Add a space if size_expression exists, otherwise just dimension_expression
            if size_dim_str:
                size_dim_str += " "
            size_dim_str += self.dimension_expression

        # If it's a struct member, prepend the struct name
        struct_prefix = f"{self.struct_name}::" if self.struct_name else ""

        # Format: [struct_name::]type [size_expression][ dimension_expression] identifier [= expression]
        output = f"{struct_prefix}{type_str} {size_dim_str} {self.identifier}"
        if self.expression:
            output += f" = {self.expression}"

        # Clean up extra spaces if size_dim_str is empty
        return " ".join(output.split())

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the Declaration object.
        This includes key attributes for debugging and introspection, making it easy
        to reconstruct the object's state.
        """
        # Using getattr for 'sequence' to handle cases where 'Basic' might not always
        # guarantee its presence, though it typically should.
        return (
            f"Declaration(data_type={self.data_type!r}, "
            f"identifier={self.identifier!r}, "
            f"expression={self.expression!r}, "
            f"size_expression={self.size_expression!r}, "
            f"size={self.size!r}, "
            f"dimension_expression={self.dimension_expression!r}, "
            f"dimension_size={self.dimension_size!r}, "
            f"source_interval={self.source_interval!r}, "
            f"element_type={self.element_type!r}, "
            f"action={self.action!r}, "
            f"struct_name={self.struct_name!r}, "
            f"name_space_level={self.number!r}, "  # Use self.number which stores name_space_level
            f"file_path={self.file_path!r}, "
            f"sequence={getattr(self, 'sequence', 'N/A')!r})"
        )


class DeclarationArray(BasicArray):
    """
    A specialized array for managing a collection of `Declaration` objects.

    This class extends `BasicArray`, providing core functionalities for
    adding, retrieving, and manipulating `Declaration` instances. It includes
    methods for filtering declarations, performing uniqueness checks, and
    utility functions for name replacement and specific declaration retrieval.
    """

    def __init__(self):
        """
        Initializes a new `DeclarationArray` instance.
        It configures the array to specifically hold objects of type `Declaration`.
        """
        super().__init__(Declaration)

    def getElement(self, identifier) -> List[Declaration]:
        return super().getElement(identifier)

    def copy(self) -> "DeclarationArray":
        """
        Creates a deep copy of the current `DeclarationArray` instance.
        This ensures that all `Declaration` objects within the array are also
        independently copied, preventing shared references and enabling
        safe modifications to the copy without affecting the original.

        Returns:
            DeclarationArray: A new `DeclarationArray` object with independent
                              copies of its `Declaration` elements.
        """
        new_array: DeclarationArray = DeclarationArray()  # Corrected typo 'new_aray'
        for element in self.getElements():
            new_array.addElement(
                element.copy()
            )  # Ensures deep copy of each Declaration
        return new_array

    def getElementByIndex(self, index: int) -> Declaration:
        """
        Retrieves a `Declaration` object from the array by its index.

        Args:
            index (int): The zero-based index of the desired element.

        Returns:
            Declaration: The `Declaration` object at the specified index.

        Raises:
            IndexError: If the index is out of bounds.
        """
        # BasicArray is expected to manage 'self.elements' list.
        return self.elements[index]

    def getElementsIE(
        self,
        include: Optional[ElementsTypes] = None,
        exclude: Optional[ElementsTypes] = None,
        include_identifier: Optional[str] = None,
        exclude_identifier: Optional[str] = None,
        file_path: Optional[str] = None,
        data_type_include: Optional[DeclTypes] = None,  # Corrected typo 'incude'
        data_type_exclude: Optional[DeclTypes] = None,
    ) -> "DeclarationArray":
        """
        Filters and retrieves `Declaration` elements based on specified inclusion/exclusion criteria.
        This method allows filtering by element type, identifier, file path, and data type.

        Args:
            include (Optional[ElementsTypes]): If provided, only include declarations
                                               of this specific `ElementsTypes`.
            exclude (Optional[ElementsTypes]): If provided, exclude declarations
                                               of this specific `ElementsTypes`.
            include_identifier (Optional[str]): If provided, only include declarations
                                                matching this identifier.
            exclude_identifier (Optional[str]): If provided, exclude declarations
                                                matching this identifier.
            file_path (Optional[str]): If provided, only include declarations
                                       originating from this specific file path.
            data_type_include (Optional[DeclTypes]): If provided, only include declarations
                                                     of this specific `DeclTypes`.
            data_type_exclude (Optional[DeclTypes]): If provided, exclude declarations
                                                     of this specific `DeclTypes`.

        Returns:
            DeclarationArray: A new `DeclarationArray` containing only the filtered elements.
                              Returns a deep copy of the original array if no filters are applied.
        """
        result_array: DeclarationArray = DeclarationArray()

        # If no filters are specified, return a deep copy of all elements for consistency.
        if all(
            arg is None
            for arg in [
                include,
                exclude,
                include_identifier,
                exclude_identifier,
                file_path,
                data_type_include,
                data_type_exclude,
            ]
        ):
            return self.copy()

        for element in self.elements:
            # Apply exclusion filters first (higher priority)
            if exclude is not None and element.element_type is exclude:
                continue
            if (
                exclude_identifier is not None
                and element.identifier == exclude_identifier
            ):
                continue
            if data_type_exclude is not None and element.data_type is data_type_exclude:
                continue

            # Apply inclusion filters
            if include is not None and element.element_type is not include:
                continue
            if (
                include_identifier is not None
                and element.identifier != include_identifier
            ):
                continue
            if file_path is not None and element.file_path != file_path:
                continue
            if (
                data_type_include is not None
                and element.data_type is not data_type_include
            ):
                continue

            # If the element passes all filters, add it to the result.
            result_array.addElement(element)

        return result_array

    # Note: This `addElement` method overrides the one inherited from BasicArray.
    # It includes custom uniqueness logic and sorting.
    def addElement(self, new_element: Declaration) -> Tuple[bool, Optional[int]]:
        """
        Adds a new `Declaration` object to the array.
        Before adding, it checks if a similar element (based on identifier,
        source interval, and namespace level) already exists. If it does,
        it prevents duplication. After adding, it sorts the elements.

        Args:
            new_element (Declaration): The `Declaration` object to be added.

        Returns:
            Tuple[bool, Optional[int]]: A tuple where:
                - The first element is `True` if the element was added successfully
                  (i.e., it was unique), `False` otherwise.
                - The second element is the index of the added or existing element,
                  or `None` if the element was not added due to a type error.

        Raises:
            TypeError: If `new_element` is not an instance of `Declaration`
                       (or the `element_type` specified in `BasicArray`).
        """
        if not isinstance(new_element, self.element_type):
            raise TypeError(
                f"Object should be of type {self.element_type} but you passed an "
                f"object of type {type(new_element)}. Object: {new_element}"
            )

        is_unique_element: Optional[Declaration] = None
        for element in self.elements:
            # Check for uniqueness based on identifier OR source_interval AND namespace level.
            # This logic implies that if two declarations have the same identifier OR
            # same source interval AND same namespace level, they are considered duplicates.
            if (
                element.identifier == new_element.identifier
                or element.source_interval == new_element.source_interval
            ) and element.number == new_element.number:  # Assuming 'number' stores name_space_level
                is_unique_element = element
                break

        if is_unique_element is not None:
            # Element already exists, return False and its index.
            # Assumes getElementIndex exists and works correctly.
            return (False, self.getElementIndex(is_unique_element.identifier))

        # Add the new element if unique.
        self.elements.append(new_element)

        # Return True and the index of the newly added element.
        return (True, self.getElementIndex(new_element.identifier))

    def getDeclarationsWithExpressions(self) -> List[Declaration]:
        """
        Retrieves a list of `Declaration` objects that have non-empty expressions
        and are not of type `DeclTypes.ENUM_TYPE`.

        Returns:
            List[Declaration]: A list of filtered `Declaration` objects.
        """
        result: List[Declaration] = []
        for element in self.elements:
            if len(element.expression) > 0 and element.data_type != DeclTypes.ENUM_TYPE:
                result.append(element)
        return result

    def getInputPorts(self) -> List[Declaration]:
        """
        Retrieves a list of `Declaration` objects that represent input ports.

        Returns:
            List[Declaration]: A list of `Declaration` objects where `data_type` is `DeclTypes.INPORT`.
        """
        result: List[Declaration] = []
        for element in self.elements:
            if element.data_type == DeclTypes.INPORT:
                result.append(element)
        return result

    def replaceDeclName(self, expression: str) -> Tuple[str, Optional[Declaration]]:
        """
        Replaces the first occurrence of a declared variable's identifier in a given
        expression with its "name" (as returned by `element.getName()`).
        This method iterates through declarations and stops after the first replacement.

        Args:
            expression (str): The string expression in which to perform the replacement.

        Returns:
            Tuple[str, Optional[Declaration]]: A tuple containing:
                - The modified expression string.
                - The `Declaration` object whose identifier was replaced, or `None` if no replacement occurred.
        """
        decl: Optional[Declaration] = None
        modified_expression = expression  # Use a new variable to build the result

        for element in self.elements:
            # Create a regex pattern to match the whole word (using \b for word boundaries)
            pattern = r"\b" + re.escape(element.identifier) + r"\b"
            # Perform substitution and get the count of replacements

            new_expression, count = re.subn(
                pattern, element.getName(), modified_expression, count=1
            )  # Limit to 1 replacement

            if count > 0:
                modified_expression = new_expression
                decl = element
                break  # Stop after the first successful replacement

        return modified_expression, decl

    def replaceDeclNames(self, expression: str) -> str:
        """
        Replaces all occurrences of declared variable identifiers in a given
        expression with their "names" (as returned by `element.getName()`).
        This method iterates through all declarations and applies all possible replacements.
        It is assumed that the order of `self.elements` (sorted by identifier length)
        helps in correct replacement of longer names before shorter, overlapping ones.

        Args:
            expression (str): The string expression in which to perform the replacements.

        Returns:
            str: The modified expression string with all identifiers replaced.
        """
        modified_expression = expression
        for element in self.elements:
            # Create a regex pattern to match the whole word (using \b for word boundaries)
            pattern = r"\b" + re.escape(element.identifier) + r"\b"
            # Perform substitution. re.subn returns (new_string, count), we only need new_string
            modified_expression, _ = re.subn(
                pattern, element.getName(), modified_expression
            )

        return modified_expression

    def findDeclWithDimensionByName(  # Corrected typo 'Dimention'
        self,
        identifier: str,
    ) -> Optional[Declaration]:
        """
        Finds a `Declaration` object by its identifier if it also has a dimension size greater than zero.

        Args:
            identifier (str): The identifier (name) of the declaration to search for.

        Returns:
            Optional[Declaration]: The `Declaration` object if found and it has a dimension,
                                   otherwise `None`.
        """
        # Assumes getElement(identifier) is a method inherited from BasicArray or defined elsewhere.
        element = self.getElement(identifier)
        if element is not None and element.dimension_size > 0:
            return element
        return None

    def logAgentsTypes2Aplan(self, logger: AplanLogger):
        decls = self.getElementsIE(data_type_exclude=DeclTypes.ENUM_TYPE)
        element: Declaration = None
        length = self.__len__()
        if length == 0:
            logger.env("\t\t\tNil")
            return
        
        last = length - 1
        for index in range(length):
            element = self.elements[index]
            if element.data_type is not DeclTypes.ENUM_TYPE:
                element.logAgentsTypes2Aplan(logger)
            if index < last:
                logger.env(",")
            elif index == last:
                logger.env("")

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `DeclarationArray` object.
        This provides a clear and concise view of the array's contents for debugging.
        """
        return f"DeclarationArray(\n{self.elements!r}\n)"

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of the `DeclarationArray`.
        Each declaration is represented on a new line.
        """
        return "\n".join(str(decl) for decl in self.elements)

    def __iter__(self):
        """
        Makes the `DeclarationArray` iterable, allowing direct iteration over its elements
        (e.g., `for decl in my_decl_array:`).
        """
        return iter(self.elements)

    def __getitem__(self, index: int) -> Declaration:
        """
        Enables direct access to elements using square brackets (e.g., `my_array[0]`).

        Args:
            index (int): The index of the element to retrieve.

        Returns:
            Declaration: The element at the specified index.
        """
        return self.elements[index]
