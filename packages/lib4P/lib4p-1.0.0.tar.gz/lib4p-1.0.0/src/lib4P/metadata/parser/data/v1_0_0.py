from .v0_0_0 import Parser as PreviousParser
from .. import parser_manager as ParserManager
from ...interface.data_interface import IData
from ...data import Data


class Parser(PreviousParser):  # ParserInterface already inherits from PreviousParser

    version = (1, 0, 0)

    def __init__(self):
        PreviousParser.__init__(self)

        self.sub_parsers["filename"] = self.parse_filename
        self.sub_parsers["plot_id"] = self.parse_plot_id
        self.sub_parsers["sensor_id"] = self.parse_sensor_id

    def to_dict(self, data, version=None):
        if not isinstance(data, IData):
            raise TypeError(f"Argument 'data' must be of type {IData}, type {type(data)} found")

        dic = super().to_dict(data, version=version)
        dic["filename"] = data.get_filename()
        dic["plot_id"] = data.get_plot().get_id()
        dic["sensor_id"] = data.get_sensor().get_id()

        return dic

    def parse_plot_id(self, plot_id, version=None):
        return "plot_id", plot_id

    def parse_sensor_id(self, sensor_id, version=None):
        return "sensor_id", sensor_id


ParserManager.register("data", Parser.version, Parser())
ParserManager.register(IData, Parser.version, Parser())
ParserManager.register(Data, Parser.version, Parser())
