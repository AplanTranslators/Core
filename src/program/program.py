from pathlib import Path
from ..utils.counters import Counters
from ..logger.logger import AplanLogger, Logger
from ..utils.string_formater import StringFormater
from ..program.beh import create_Beh_File
from ..program.action import create_Action_File
from ..program.env import generateEnv
from ..program.evt import generateEvt
from ..singleton.singleton import SingletonMeta
from ..classes.typedef import TypedefArray
from ..classes.design_unit import DesignUnitArray
from ..classes.design_unit_call import DesignUnitCallArray
import os


class Program(metaclass=SingletonMeta):
    str_formater = StringFormater()
    counters = Counters()

    def __init__(self, result_path: Path | None = None) -> None:

        self._design_units: DesignUnitArray = DesignUnitArray()
        self._design_units_calls: DesignUnitCallArray = DesignUnitCallArray()
        self._typedefs: TypedefArray = TypedefArray()

        self.logger: Logger = Logger(self.__class__.__qualname__)
        self.aplan_logger = AplanLogger(result_path)
        self.file_path: Path | None = None

    @property
    def result_path(self) -> Path:
        return self.aplan_logger.result_path

    @property
    def design_units(self) -> DesignUnitArray:
        return self._design_units

    @property
    def design_units_calls(self) -> DesignUnitCallArray:
        return self._design_units_calls

    @property
    def typedefs(self) -> TypedefArray:
        return self._typedefs

    def generateAplan(self):
        generateEvt(self)
        generateEnv(self)
        create_Action_File(self)
        create_Beh_File(self)
        self.logger.info(
            "The translation was successfully completed! \n", "bold_yellow"
        )
        self.counters.deinit()
