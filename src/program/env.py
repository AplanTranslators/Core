from typing import TYPE_CHECKING

from Core.src.logger.logger import LOG_NL

from ..classes.declarations import DeclTypes

from ..classes.element_types import ElementsTypes

if TYPE_CHECKING:
    from program import Program


def generateEnv(self: "Program"):
    self.aplan_logger.env("environment (")

    # ----------------------------------
    # Types
    # ----------------------------------
    self.aplan_logger.env("\ttypes : obj (")
    sub_env = ""
    decls = self.typedefs.getElementsIE()

    for design_unit in self.design_units.getElements():
        decls += design_unit.typedefs.getElementsIE()

    sub_env += str(decls)

    if len(sub_env) > 0:
        self.aplan_logger.env(sub_env)
    else:
        self.aplan_logger.env("\t\t\tNil")

    self.aplan_logger.env("\t);")

    # ----------------------------------
    # Attributes
    # ----------------------------------
    self.aplan_logger.env("\tattributes : obj (Nil);")

    # ----------------------------------
    # Agents types
    # ----------------------------------

    self.aplan_logger.env("\tagent_types : obj (")

    # Генеруємо рядки для кожного design_unit
    self.design_units.logAgentsTypes2Aplan(self.aplan_logger)

    self.aplan_logger.env("\t\tENVIRONMENT:obj(Nil)")
    self.aplan_logger.env("\t);")

    # ----------------------------------
    # Agents
    # ----------------------------------
    self.aplan_logger.env("\tagents : obj (")
    self.design_units.logAgentsObjs2Aplan(self.aplan_logger)

    self.aplan_logger.env("\t\tENVIRONMENT : obj (env)")
    self.aplan_logger.env("\t);")

    # ----------------------------------
    # Axioms
    # ----------------------------------
    self.aplan_logger.env("\taxioms : obj (Nil);")

    # ----------------------------------
    # Logic formula
    # ----------------------------------
    self.aplan_logger.env("\tlogic_formula : obj (1)")
    self.aplan_logger.env(");")

    self.logger.info(".env_descript file created ", "purple")
