from ..logger.logger import AplanLogger
from .parametrs import ParametrArray
from .processed import ProcessedElementArray
from .actions import ActionArray
from .typedef import TypedefArray
from .value_parametrs import ValueParametrArray
from .protocols import ProtocolArray
from .declarations import DeclTypes, DeclarationArray
from .structure import StructureArray
from .basic import Basic, BasicArray
from .element_types import ElementsTypes
from .tasks import TaskArray
from typing import Any, List, Optional, Tuple, Union
import re


class DesignUnit(Basic):
    """
    Represents a hardware design_unit, a software class, or a similar encapsulated entity
    within a design. It aggregates various types of elements, including declarations,
    typedefs, actions, structures, parameters, and nested design_units/objects,
    providing a holistic view of a design component.
    """

    def __init__(
        self,
        identifier: str = "placeholder",
        source_interval: Tuple[int, int] = (0, 0),
        ident_uniq_name: str = "placeholder",  # Changed type hint from Any to str
        element_type: "ElementsTypes" = ElementsTypes.MODULE_ELEMENT,
    ):
        """
        Initializes a new `DesignUnit` instance.

        Args:
            identifier (str): The common name of the design_unit (e.g., "my_fifo", "Processor").
            source_interval (Tuple[int, int]): The (start, end) character positions
                                                in the original source file where the design_unit is defined.
            ident_uniq_name (str): A unique identifier for this design_unit across the entire design,
                                   often including hierarchical path information.
            element_type (ElementsTypes, optional): The specific type of element this design_unit represents.
                                                    Defaults to `ElementsTypes.MODULE_ELEMENT`.
                                                    Can be `ElementsTypes.CLASS_ELEMENT` for software classes.
            name_space_level (int, optional): The nesting level of this design_unit within the design hierarchy.
                                              Defaults to 0 (top-level).
        """
        # Convert identifier to uppercase immediately for internal consistency.
        # This means the original case is not preserved in self.identifier.
        super().__init__(identifier.upper(), source_interval, element_type)
        self.ident_uniq_name: str = ident_uniq_name

        # Cache uppercase versions for efficiency if used frequently in this case
        self.identifier_upper: str = (
            self.identifier
        )  # Already upper from super().__init__
        self.ident_uniq_name_upper: str = self.ident_uniq_name.upper()

        self.number: int = self.counters.get(self.counters.types.STRUCT_COUNTER)
        self.counters.incriese(self.counters.types.STRUCT_COUNTER)
        # Initialize collections for various sub-elements within the design_unit.
        # These are instances of custom array classes, enabling structured storage and operations.
        self.declarations: "DeclarationArray" = DeclarationArray()
        self.typedefs: "TypedefArray" = TypedefArray()
        self.actions: "ActionArray" = ActionArray()
        self.structures: "StructureArray" = StructureArray()
        self.out_of_block_elements: "ProtocolArray" = (
            ProtocolArray()
        )  # Elements representing design_unit's main protocol
        self.value_parametrs: "ValueParametrArray" = ValueParametrArray()
        self.input_parametrs: "ParametrArray" = ParametrArray()
        self.processed_elements: "ProcessedElementArray" = ProcessedElementArray()
        self.tasks: "TaskArray" = TaskArray()
        self.packages_and_objects: "DesignUnitArray" = (
            DesignUnitArray()
        )  # For nested design_units or class instances

    def setSourceInterval(self, source_interval: Tuple[int, int]):
        self.source_interval = source_interval

    def setIdentifier(self, new_identifier: str, new_ident_uniq_name: str):
        """
        Updates the identifier and unique identifier of the DesignUnit.

        Args:
            new_identifier (str): The new common name for the design unit.
            new_ident_uniq_name (str): The new unique identifier for the design unit.
        """
        self.identifier = new_identifier.upper()
        self.ident_uniq_name = new_ident_uniq_name

        # Оновлюємо кешовані версії
        self.identifier_upper = self.identifier
        self.ident_uniq_name_upper = self.ident_uniq_name.upper()

    # Type hint for copy return type: Self for Python 3.11+, else forward reference str
    def copyPart(self) -> "DesignUnit":
        """
        Creates a 'partial' shallow copy of the `DesignUnit` instance.
        Most of the contained `BasicArray` objects are copied by reference (shallow copy),
        meaning the new design_unit will share these collections with the original.
        Modifications to these shared arrays in the copied design_unit will affect the original.

        This method is useful when only the design_unit's core attributes and
        references to its top-level element arrays are needed, without duplicating
        the potentially large contents of those arrays.

        Returns:
            DesignUnit: A new `DesignUnit` object with shared (shallow-copied) internal arrays.
        """
        design_unit = DesignUnit(
            self.identifier,
            self.source_interval,
            self.ident_uniq_name,
            self.element_type,
            self.number,  # Pass name_space_level to copy constructor
        )
        design_unit.number = self.number  # Ensure number is also copied

        # Shallow copy of references to the internal arrays
        design_unit.declarations = self.declarations
        design_unit.actions = self.actions
        design_unit.structures = self.structures
        design_unit.out_of_block_elements = self.out_of_block_elements
        design_unit.value_parametrs = self.value_parametrs
        design_unit.processed_elements = self.processed_elements
        design_unit.tasks = self.tasks
        design_unit.packages_and_objects = self.packages_and_objects
        # Missing typedefs and input_parametrs from shallow copy

        return design_unit

    # Type hint for copy return type: Self for Python 3.11+, else forward reference str
    def copy(self) -> "DesignUnit":
        """
        Creates a deep copy of the `DesignUnit` instance.
        All contained `BasicArray` objects are also deep-copied by calling their
        respective `.copy()` methods. This ensures that the new design_unit instance
        and all its contents are independent of the original.

        Additionally, it calls `updateLinks` on certain copied arrays (`structures`,
        `out_of_block_elements`) to ensure their internal references correctly
        point to the newly created `DesignUnit` instance.

        Returns:
            DesignUnit: A completely independent deep copy of the `DesignUnit` object.
        """
        design_unit = DesignUnit(
            self.identifier,
            self.source_interval,
            self.ident_uniq_name,
            self.element_type,
            self.number,  # Pass name_space_level to copy constructor
        )
        design_unit.number = self.number  # Ensure number is also copied

        # Deep copy all contained BasicArray instances
        design_unit.declarations = self.declarations.copy()
        design_unit.typedefs = self.typedefs.copy()  # Added typedefs to deep copy
        design_unit.actions = self.actions.copy()
        design_unit.structures = self.structures.copy()
        # After copying structures, update their internal links to the new design_unit instance
        design_unit.structures.updateLinks(
            design_unit
        )  # Assumes StructureArray has updateLinks method

        design_unit.out_of_block_elements = self.out_of_block_elements.copy()
        # After copying out_of_block_elements, update their internal links to the new design_unit instance
        design_unit.out_of_block_elements.updateLinks(
            design_unit
        )  # Assumes ProtocolArray has updateLinks method

        design_unit.value_parametrs = self.value_parametrs.copy()
        design_unit.input_parametrs = (
            self.input_parametrs.copy()
        )  # Added input_parametrs to deep copy
        design_unit.processed_elements = self.processed_elements.copy()
        design_unit.tasks = self.tasks.copy()
        design_unit.packages_and_objects = self.packages_and_objects.copy()

        return design_unit

    def findAndChangeNamesToAgentAttrCall(
        self, input_string: str, packages: Optional[List["DesignUnit"]] = None
    ) -> str:
        """
        Transforms identifiers in a given input string to an "agent attribute call" format.
        This means prefixing identifiers with either "object_pointer." (for classes)
        or the design_unit's unique name (for regular design_units).
        It processes both the current design_unit's declarations and, optionally,
        declarations from a list of external packages/design_units.

        Args:
            input_string (str): The string in which identifiers need to be transformed.
            packages (Optional[List[DesignUnit]]): An optional list of other `DesignUnit` instances
                                                (e.g., imported packages) whose declarations
                                                should also be considered for transformation.

        Returns:
            str: The transformed string with identifiers prefixed.
        """
        # Determine the base identifier for attribute calls
        if self.element_type is ElementsTypes.CLASS_ELEMENT:
            # For class elements, typically use a generic "object_pointer"
            ident_prefix = "object_pointer"
        else:
            # For regular design_units, use the design_unit's unique name
            ident_prefix = self.ident_uniq_name

        # Process declarations within the current design_unit
        for elem in self.declarations.getElements():
            # Use word boundaries (\b) to ensure only whole words are replaced
            # Use `elem.getName()` if it consistently provides the string to be used in the output.
            # Otherwise, use `elem.identifier`. Assuming getName is the desired output format.
            input_string = re.sub(
                r"\b{}\b".format(re.escape(elem.identifier)),
                "{}.{}".format(ident_prefix, elem.getName()),  # Using getName()
                input_string,
            )

        # Optionally process declarations from external packages/design_units
        if packages is not None:
            for package in packages:
                # Determine the prefix for elements from the current package
                if self.element_type is ElementsTypes.CLASS_ELEMENT:
                    package_ident_prefix = (
                        "object_pointer"  # Still object_pointer for class context
                    )
                else:
                    package_ident_prefix = package.ident_uniq_name

                for elem in package.declarations.getElements():
                    input_string = re.sub(
                        r"\b{}\b".format(re.escape(elem.identifier)),
                        "{}.{}".format(
                            package_ident_prefix, elem.identifier
                        ),  # Using identifier here
                        input_string,
                    )
        return input_string

    def isIncludeOutOfBlockElements(self) -> bool:
        """
        Checks if this design_unit contains any "out-of-block" elements (protocol elements).

        Returns:
            bool: True if `out_of_block_elements` array is not empty, False otherwise.
        """
        return len(self.out_of_block_elements) > 0  # Use len() for efficiency

    def findElementByIdentifier(self, identifier: str) -> List[Any]:
        """
        Searches across various internal collections (`typedefs`, `declarations`,
        `tasks`, `value_parametrs`) for elements matching the given identifier.
        This method can return a heterogeneous list of different element types
        and their associated sub-elements (e.g., a task and its structure/elements).

        Args:
            identifier (str): The identifier (name) of the element to find.

        Returns:
            List[Any]: A list of all elements found with the matching identifier,
                       potentially including related sub-elements. The list can contain
                       objects of different types (Typedef, Declaration, Task, ValueParametr,
                       and potentially Action or Structure elements).
        """
        result: List[Any] = []

        # Search in typedefs
        for element in self.typedefs.getElements():
            if element.identifier == identifier:
                result.append(element)

        # Search in declarations
        for element in self.declarations.getElements():
            if element.identifier == identifier:
                result.append(element)
                # If it's not an ENUM type and has an expression, also include its associated action.
                # This assumes Declaration objects can have an 'action' attribute.
                if (
                    element.data_type is not DeclTypes.ENUM_TYPE
                    and hasattr(element, "expression")
                    and len(element.expression)
                    > 0  # Check if expression exists and is not empty
                    and hasattr(element, "action")  # Check if action attribute exists
                ):
                    result.append(element.action)

        # Search in tasks
        for element in self.tasks.getElements():
            if element.identifier == identifier:
                result.append(element)
                # For tasks, also include its associated structure and its internal elements.
                if hasattr(element, "structure") and element.structure is not None:
                    result.append(element.structure)
                    if (
                        hasattr(element.structure, "elements")
                        and element.structure.elements is not None
                    ):
                        for struct_element in element.structure.elements.getElements():
                            result.append(struct_element)

        # Search in value_parametrs
        for element in self.value_parametrs.getElements():
            if element.identifier == identifier:
                result.append(element)

        return result

    def getInputParametrs(self) -> str:
        """
        Generates a parenthesized string of input parameters for the design_unit,
        formatted as `(param1, param2, ...)`.

        Returns:
            str: A string like "(param1, param2)" if input parameters exist,
                 otherwise an empty string.
        """
        # Checks if input_parametrs array exists and is not empty
        if self.input_parametrs and len(self.input_parametrs) > 0:
            return f"({str(self.input_parametrs)})"  # Assumes ParametrArray's __str__ is suitable
        return ""

    def _format_main_protocol_section(self, parametrs: str) -> Tuple[str, str, bool]:
        """
        Helper method to format the 'MAIN_PROTOCOL' section of the design_unit's behavior.
        This section represents the primary operational flow of the design_unit,
        combining `out_of_block_elements` with specific separators (`;` or `||`)
        and conditional parentheses.

        Args:
            parametrs (str): The formatted input parameters string (e.g., "(a, b)").

        Returns:
            Tuple[str, str, bool]:
                - str: The full formatted 'MAIN_PROTOCOL' string (e.g., "MAIN_MOD_NAME = (p1; p2 || (p3))").
                - str: The name of the main protocol part (e.g., "MAIN_MOD_NAME").
                - bool: True if the main protocol section has content, False otherwise.
        """
        main_protocol_body_parts: List[str] = []
        protocols_list = (
            self.out_of_block_elements.getElements()
        )  # Use getElements() for consistency

        # Ensure elements are sorted by a 'sequence' attribute, crucial for protocol order
        protocols_list.sort(
            key=lambda prot: prot.sequence if hasattr(prot, "sequence") else 0
        )

        for index, element in enumerate(protocols_list):
            if index > 0:
                prev_element = protocols_list[index - 1]

                # Determine separator based on current element type
                # Aplan format: MODULE_CALL_ELEMENT typically uses ';', others use '||'
                if element.element_type == ElementsTypes.MODULE_CALL_ELEMENT:
                    main_protocol_body_parts.append(";")
                else:
                    main_protocol_body_parts.append(" || ")

                # Add opening parenthesis for specific transitions:
                # If previous element was an assignment OUT_OF_BLOCK and current is a design_unit call/assign
                if (
                    prev_element.element_type
                    == ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT
                ) and (
                    element.element_type == ElementsTypes.MODULE_CALL_ELEMENT
                    or element.element_type == ElementsTypes.MODULE_ASSIGN_ELEMENT
                ):
                    main_protocol_body_parts.append("(")

            # Append the identifier of the current element
            main_protocol_body_parts.append(element.getName())

            # Add closing parenthesis for specific transitions:
            # If next element is an assignment OUT_OF_BLOCK and current is a design_unit call/assign
            if index + 1 < len(protocols_list):
                next_element = protocols_list[index + 1]
                if (
                    next_element.element_type
                    == ElementsTypes.ASSIGN_OUT_OF_BLOCK_ELEMENT
                ) and (
                    element.element_type == ElementsTypes.MODULE_CALL_ELEMENT
                    or element.element_type == ElementsTypes.MODULE_ASSIGN_ELEMENT
                ):
                    main_protocol_body_parts.append(")")

        main_protocol_body_str = "".join(main_protocol_body_parts)

        main_protocol_full_str = ""
        main_protocol_part_name = ""
        main_flag = False

        if main_protocol_body_str:
            main_flag = True
            # Construct the unique name for the main protocol
            main_protocol_part_name = f"MAIN_{self.ident_uniq_name_upper}{parametrs}"
            main_protocol_full_str = (
                f"{main_protocol_part_name} = ({main_protocol_body_str})"
            )
        return main_protocol_full_str, main_protocol_part_name, main_flag

    def _format_always_part_section(self) -> Tuple[str, str, bool]:
        """
        Helper method to format the 'ALWAYS_PART' section.
        This section typically aggregates conditions for always-active behaviors
        (e.g., sensitive lists or continuous assignments), joined by '||'.

        Returns:
            Tuple[str, str, bool]:
                - str: The body of the 'ALWAYS_PART' section (e.g., "cond1 || cond2").
                - str: A placeholder name (not directly used as a protocol name here).
                - bool: True if the always part has content, False otherwise.
        """
        # Assumes structures.getAlwaysList() returns a list of elements suitable for this format
        always_list = self.structures.getAlwaysList()
        always_part_body_parts: List[str] = []
        always_flag = False

        for index, element in enumerate(always_list):
            if index > 0:
                always_part_body_parts.append(" || ")
            # Assumes element has a getSensetiveForB0() method returning a string
            if hasattr(element, "getSensetiveForB0"):
                always_part_body_parts.append(element.getSensetiveForB0())
            else:
                # Fallback if method not found, log warning or represent as identifier
                always_part_body_parts.append(
                    str(element.identifier)
                )  # Assuming identifier exists

        always_part_body_str = "".join(always_part_body_parts)
        if always_part_body_str:
            always_flag = True
        return (
            always_part_body_str,
            (
                "ALWAYS_PART_NAME_PLACEHOLDER" if always_flag else ""
            ),  # Name is a placeholder here
            always_flag,
        )

    def _format_struct_part_section(self) -> Tuple[str, str, bool]:
        """
        Helper method to format the 'STRUCT_PART' section.
        This section typically aggregates conditions or names related to structures
        that are not part of "always" blocks, joined by '||'.

        Returns:
            Tuple[str, str, bool]:
                - str: The body of the 'STRUCT_PART' section (e.g., "struct1_name || struct2_name").
                - str: A placeholder name (not directly used as a protocol name here).
                - bool: True if the struct part has content, False otherwise.
        """
        # Assumes structures.getNoAlwaysStructures() returns a list of elements suitable for this format
        structs_list = self.structures.getNoAlwaysStructures()
        struct_part_body_parts: List[str] = []
        struct_flag = False

        for index, element in enumerate(structs_list):
            if index > 0:
                struct_part_body_parts.append(" || ")
            # Assumes element has a getName() method returning a string
            if hasattr(element, "getName"):
                struct_part_body_parts.append(element.getName())
            else:
                struct_part_body_parts.append(str(element.identifier))  # Fallback

        struct_part_body_str = "".join(struct_part_body_parts)
        if struct_part_body_str:
            struct_flag = True
        return (
            struct_part_body_str,
            (
                "STRUCT_PART_NAME_PLACEHOLDER" if struct_flag else ""
            ),  # Name is a placeholder here
            struct_flag,
        )

    def _format_init_protocol_section(self, parametrs: str) -> Tuple[str, str, bool]:
        """
        Helper method to format the 'INIT_PROTOCOL' section.
        This section typically contains initialization expressions for declarations
        within the design_unit, joined by '.'.

        Args:
            parametrs (str): The formatted input parameters string (e.g., "(a, b)").

        Returns:
            Tuple[str, str, bool]:
                - str: The full formatted 'INIT_PROTOCOL' string.
                - str: The name of the init protocol part.
                - bool: True if the init protocol section has content, False otherwise.
        """
        # Assumes declarations.getDeclarationsWithExpressions() returns an array/list
        init_protocols_array = self.declarations.getDeclarationsWithExpressions()
        # Sort by sequence for consistent output order
        init_protocols_array.sort(
            key=lambda prot: prot.sequence if hasattr(prot, "sequence") else 0
        )

        init_protocol_body_parts: List[str] = []
        init_flag = False

        for index, element in enumerate(init_protocols_array):
            if index > 0:
                init_protocol_body_parts.append(".")  # Separator for init expressions
            # Assumes element has an 'expression' attribute that is a string
            if hasattr(element, "expression") and element.expression is not None:
                init_protocol_body_parts.append(element.expression)
            else:
                init_protocol_body_parts.append(
                    f"/* Missing Expression for {element.identifier} */"
                )

        init_protocol_body_str = "".join(init_protocol_body_parts)

        init_protocol_full_str = ""
        init_protocol_part_name = ""

        if init_protocol_body_str:
            init_flag = True
            # Construct the unique name for the init protocol
            init_protocol_part_name = f"INIT_{self.ident_uniq_name_upper}{parametrs}"
            init_protocol_full_str = (
                f"{init_protocol_part_name} = {init_protocol_body_str}"
            )
        return init_protocol_full_str, init_protocol_part_name, init_flag

    def getBehInitProtocols(self) -> str:
        """
        Generates a comprehensive behavioral and initialization protocol string
        for the design_unit, suitable for output in a specific Aplan-like format.
        It combines sections for MAIN protocol, ALWAYS part, STRUCT part, and INIT protocol,
        and then constructs a top-level B0 protocol that orchestrates these parts.

        The order of assembly within B0 is typically INIT || STRUCT || ALWAYS || MAIN.

        Returns:
            str: The fully formatted behavioral and initialization protocol string.
                 The string will not end with a trailing comma or newline.
        """
        result_lines: List[str] = []
        parametrs = self.getInputParametrs()  # Get formatted input parameters

        # 1. Format MAIN PROTOCOL Section
        main_protocol_str, main_protocol_part_name, main_flag = (
            self._format_main_protocol_section(parametrs)
        )
        if main_protocol_str:
            result_lines.append(
                f"{main_protocol_str},"
            )  # Add comma at the end of MAIN protocol line

        # 2. Format ALWAYS PART Section (gets body content)
        always_part_body_str, _, always_flag = self._format_always_part_section()

        # 3. Format STRUCT PART Section (gets body content)
        struct_part_body_str, _, struct_flag = self._format_struct_part_section()

        # 4. Format INIT PROTOCOL Section
        init_protocol_str, init_protocol_part_name, init_flag = (
            self._format_init_protocol_section(parametrs)
        )
        if init_protocol_str:
            # INIT protocol is inserted at the beginning of the result_lines
            result_lines.insert(0, f"{init_protocol_str},")

        # 5. Assemble the B0 body by concatenating the formatted part names/bodies
        b_body_parts: List[str] = []

        # Order of concatenation for B0: INIT || STRUCT || ALWAYS || MAIN
        if init_protocol_part_name:
            b_body_parts.append(init_protocol_part_name)

        if struct_part_body_str:
            # Add ' || ' separator if there's a preceding part in B0
            if b_body_parts:
                b_body_parts.append(" || ")
            b_body_parts.append(struct_part_body_str)

        if always_part_body_str:
            # Add ' || ' separator if there's a preceding part in B0
            if b_body_parts:
                b_body_parts.append(" || ")
            b_body_parts.append(always_part_body_str)

        if main_protocol_part_name:
            # Add ' || ' separator if there's a preceding part in B0
            if b_body_parts:
                b_body_parts.append(" || ")
            b_body_parts.append(main_protocol_part_name)

        b_body = "".join(b_body_parts)
        b0_protocol_str = ""

        if b_body:
            # Construct the full B0 protocol line
            b0_protocol_str = (
                f"B_{self.ident_uniq_name_upper}{parametrs} = {{{b_body}}}"
            )
            # Add a comma to B0 if it exists, assuming it's part of a list of definitions.
            # This comma will be cleaned up by the final strip().
            b0_protocol_str += ","

        # Insert B0 at the very beginning of the overall result lines
        if b0_protocol_str:
            result_lines.insert(0, b0_protocol_str)

        # Join all collected lines with newlines, then remove any trailing commas or newlines.
        final_result = "\n".join(result_lines).strip()

        # If the final string ends with a comma (due to the ", " added to individual lines)
        # and it's the only content, it might need specific trimming.
        # The .strip() removes leading/trailing whitespace including newlines.
        # To ensure no trailing comma if it's the last actual element, we might need more specific logic.
        # if final_result.endswith(","):
        #     final_result = final_result[
        #         :-1
        #     ]  # Remove the last comma if it's the very end

        return final_result

    def logAgentsTypes2Aplan(self, logger: AplanLogger):
        if self.element_type == ElementsTypes.OBJECT_ELEMENT:
            return
        logger.env("\t\t{0} : obj (".format(self.ident_uniq_name_upper))
        self.declarations.logAgentsTypes2Aplan(logger)
        logger.env("\t\t),")

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `DesignUnit` object,
        displaying its core identifiers and type for debugging and introspection.
        """
        return (
            f"DesignUnit("
            f"identifier={self.identifier!r}, "
            f"source_interval={self.source_interval!r}, "
            f"ident_uniq_name={self.ident_uniq_name!r}, "
            f"element_type={self.element_type!r}, "
            f"name_space_level={self.number!r}"  # Use self.number as it stores name_space_level
            f")"
        )


class DesignUnitArray(BasicArray):
    """
    A specialized array for managing a collection of `DesignUnit` objects.
    This class extends `BasicArray` and provides methods for adding, finding,
    and filtering `DesignUnit` instances.
    """

    def __init__(self):
        """
        Initializes a new `DesignUnitArray` instance, specifically configured
        to store objects of type `DesignUnit`.
        """
        super().__init__(
            DesignUnit
        )  # Use string literal if DesignUnit is defined later or in a cycle

    # Type hint for copy return type: Self for Python 3.11+, else forward reference str
    def copy(self) -> "DesignUnitArray":
        """
        Creates a deep copy of the current `DesignUnitArray` instance.
        It iterates through all contained `DesignUnit` objects and adds their
        deep copies to the new array, ensuring full independence.

        Returns:
            DesignUnitArray: A new `DesignUnitArray` containing deep copies of all
                         original design_units.
        """
        new_array = DesignUnitArray()
        for element in self.elements:  # Iterate directly over the internal list
            new_array.addElement(element.copy())  # Use DesignUnit's deep copy method
        return new_array

    def findModuleByUniqIdentifier(
        self, ident_uniq_name: str
    ) -> Optional["DesignUnit"] | None:
        """
        Finds a `DesignUnit` object in the array by its unique identifier.

        Args:
            ident_uniq_name (str): The unique identifier of the design_unit to find.

        Returns:
            Optional[DesignUnit]: The `DesignUnit` object if found, otherwise None.
        """
        for element in self.elements:
            if (
                element.ident_uniq_name == ident_uniq_name
            ):  # Use '==' for string comparison
                return element
        return None

    def getElements(self) -> List["DesignUnit"]:
        """
        Returns the internal list of `DesignUnit` elements directly.

        Returns:
            List[DesignUnit]: A list of `DesignUnit` objects.
        """
        return self.elements

    def getElementByIndex(self, index: int) -> "DesignUnit":
        """
        Retrieves a `DesignUnit` object from the array by its zero-based index.

        Args:
            index (int): The index of the element to retrieve.

        Returns:
            DesignUnit: The `DesignUnit` object at the specified index.

        Raises:
            IndexError: If the index is out of bounds.
        """
        return super().getElementByIndex(index)

    def getElementsIE(
        self,
        include: Optional["ElementsTypes"] = None,
        exclude: Optional["ElementsTypes"] = None,
        include_ident_uniq_names: Optional[List[str]] = None,
        exclude_ident_uniq_name: Optional[str] = None,
    ) -> "DesignUnitArray":
        """
        Filters the `DesignUnit` objects in the array based on various criteria,
        including `element_type` and unique identifiers.

        Args:
            include (Optional[ElementsTypes]): Only include design_units with this element type.
            exclude (Optional[ElementsTypes]): Exclude design_units with this element type.
            include_ident_uniq_names (Optional[List[str]]): Only include design_units whose unique
                                                            identifier is in this list.
            exclude_ident_uniq_name (Optional[str]): Exclude design_units with this specific unique identifier.

        Returns:
            DesignUnitArray: A new `DesignUnitArray` containing only the design_units that
                         match all specified filtering criteria. If no criteria are
                         provided, a deep copy of the original array is returned.
        """
        result: "DesignUnitArray" = DesignUnitArray()

        # If no filters are specified, return a deep copy of the entire array.
        if all(
            arg is None
            for arg in [
                include,
                exclude,
                include_ident_uniq_names,
                exclude_ident_uniq_name,
            ]
        ):
            return (
                self.copy()
            )  # Return a copy to prevent accidental modification of original

        for element in self.elements:
            # Apply element_type filters
            if include is not None and element.element_type is not include:
                continue
            if exclude is not None and element.element_type is exclude:
                continue

            # Apply include unique identifier filter
            if (
                include_ident_uniq_names is not None
                and element.ident_uniq_name not in include_ident_uniq_names
            ):
                continue

            # Apply exclude unique identifier filter (use '==' for string comparison)
            if (
                exclude_ident_uniq_name is not None
                and element.ident_uniq_name == exclude_ident_uniq_name
            ):
                continue

            result.addElement(element)  # Add the element if it passes all filters
        return result

    def logAgentsTypes2Aplan(self, logger: AplanLogger):
        for design_unit in self.elements:
            design_unit.logAgentsTypes2Aplan(logger)

    def logAgentsObjs2Aplan(self, logger: AplanLogger):
        for design_unit in self.getElementsIE(
            exclude=ElementsTypes.CLASS_ELEMENT
        ).getElements():
            logger.env(
                "\t\t{0} : obj ({1}),".format(
                    design_unit.ident_uniq_name_upper,
                    design_unit.ident_uniq_name,
                )
            )

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the `DesignUnitArray` object,
        displaying the `repr` of its internal elements list for debugging.
        """
        return f"DesignUnitArray(\n{self.elements!r}\n)"

    # Add standard container methods for better usability and Pythonic behavior
    def __len__(self) -> int:
        """Returns the number of elements in the array. Enables `len(instance)`."""
        return len(self.elements)

    def __getitem__(
        self, index: Union[int, slice]
    ) -> Union["DesignUnit", List["DesignUnit"]]:
        """Allows direct indexing and slicing of the array, e.g., `array[0]` or `array[1:3]`."""
        return self.elements[index]

    def __iter__(self):
        """Makes the array iterable, allowing `for element in array_instance:`."""
        return iter(self.elements)
