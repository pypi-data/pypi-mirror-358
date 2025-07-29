from .....parser import parser_manager as ParserManager
from .....parser.sensor.v1_0_0 import Parser as BaseSensorParser
from ...camera_sensor import CameraSensor
from .v0_0_0 import Parser as PreviousParser


class Parser(PreviousParser, BaseSensorParser):

    def __init__(self):
        BaseSensorParser.__init__(self)

    def to_dict(self, data, version=None):
        if not isinstance(data, CameraSensor):
            raise TypeError(f"Argument 'data' must be of type {CameraSensor}, type {type(data)} found")

        dic = super().to_dict(data, version=version)

        return dic


ParserManager.register(CameraSensor, Parser.version, Parser())
