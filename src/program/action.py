from typing import TYPE_CHECKING
from ..classes.element_types import ElementsTypes

if TYPE_CHECKING:
    from program import Program


def create_Action_File(self: "Program"):
    # ----------------------------------
    # Actions
    # ----------------------------------
    actions = ""
    design_units = self.design_units.getElementsIE(
        exclude=ElementsTypes.OBJECT_ELEMENT
    ).getElements()
    element_strings = [unit.actions.getActionsInStrFormat() for unit in design_units]
    actions = ",\n".join(element_strings)

    self.aplan_logger.act(actions)

    self.logger.info(".act file created \n", "purple")
