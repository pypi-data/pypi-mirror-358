from .v0_0_0 import Parser as PreviousParser
from .. import parser_manager as ParserManager
from ... import Geolocation
from ...interface.geolocation_interface import IGeolocation


class Parser(PreviousParser):  # ParserInterface already inherits from PreviousParser

    version = (1, 0, 0)

    def __init__(self):
        PreviousParser.__init__(self)

        self.sub_parsers["plot_id"] = self.parse_plot_id

    def to_dict(self, data, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        if not isinstance(data, IGeolocation):
            raise TypeError(f"Argument 'data' must be of type {IGeolocation}, type {type(data)} found")

        dic = super().to_dict(data, version=version)
        dic["plot_id"] = data.get_plot().get_id()

        return dic

    def parse_plot_id(self, plot_id, version=None):
        return "plot_id", plot_id


ParserManager.register("geolocation", Parser.version, Parser())
ParserManager.register(IGeolocation, Parser.version, Parser())
ParserManager.register(Geolocation, Parser.version, Parser())
