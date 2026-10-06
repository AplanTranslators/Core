from typing import Optional, Tuple

from ..classes.node import NodeArray
from ..classes.element_types import ElementsTypes
from ..classes.structure import Structure

# from antlr4_verilog.systemverilog import SystemVerilogParser


class CaseStmt(Structure):
    """
    Represents a 'case' statement block, commonly found in hardware description
    languages like SystemVerilog.

    This class extends `Structure`, inheriting properties such as an identifier,
    source code interval, and namespace level. It specifically models the expression
    being evaluated in the case statement and manages related counters.
    """

    def __init__(
        self,
        identifier: str,
        source_interval: Tuple[int, int],
    ):
        """
        Initializes a new CaseStmt instance.

        Args:
            identifier (str): A unique string identifier for this case statement.
            source_interval (Tuple[int, int]): A tuple representing the start and end
                                                positions of the case statement in the source code.
            name_space_level (int): The nesting level of this case statement within
                                    the overall structure or namespace.
        """
        # Call the parent class (Structure) constructor.
        # It sets the element type specifically to CASE_STATEMENT_ELEMENT.
        super().__init__(
            identifier,
            source_interval,
            element_type=ElementsTypes.CASE_STATEMENT_ELEMENT,
        )
        # The expression that the case statement evaluates.
        # This is typed as a specific ANTLR4 parser context, allowing direct access
        # to the parsed syntax tree node for the expression.
        self.expr_ctx = None
        self.expr_parsed: NodeArray = NodeArray(ElementsTypes.PRECONDITION_ELEMENT)
        # 'init_case_count' stores the initial or total number of case items.
        self.init_case_count: int = 0
        # 'case_count' can be used as a mutable counter, perhaps for tracking
        # remaining case items or processed items during analysis.
        self.case_count: int = 0

    def setCaseCount(self, count: int):
        """
        Sets both the initial and current case item counts for this statement.

        Args:
            count (int): The total number of case items within this 'case' block.
        """
        self.init_case_count = count
        self.case_count = count

    def __repr__(self) -> str:
        """
        Returns a developer-friendly string representation of the CaseStmt object.
        This is useful for debugging and provides a clear view of the object's state,
        including its identifier, expression (if set), and inherited attributes like sequence.
        """
        # 'identifier' is directly from this class/inherited.
        # 'expression' might be None, so repr handles it.
        # 'sequence' is assumed to be inherited from the 'Structure' or 'Basic' base class.
        # 'sensetive' was in the original __repr__ but is not an attribute of CaseStmt.
        # It's been removed to avoid AttributeError.
        return (
            f"\tCaseStmt(identifier={self.identifier!r}, "
            f"expr_ctx={self.expr_ctx!r}, "
            f"expr_parsed={self.expr_parsed!r}, "
            f"init_case_count={self.init_case_count!r}, "
            f"case_count={self.case_count!r}, "
            f"sequence={getattr(self, 'sequence', 'N/A')!r})\n"
        )
