from .....parser import parser_manager as ParserManager
from ....image_metadata.parser.camera_sensor.v0_0_0 import Parser as BaseParser
from ...mspec_sensor import MSpecSensor


class Parser(BaseParser):

    def __init__(self):
        BaseParser.__init__(self)

        self.sub_parsers["central_wavelength"] = self.parse_central_wavelength

    def to_dict(self, data, version=None):
        if not isinstance(data, MSpecSensor):
            raise TypeError(f"Argument 'data' must be of type {MSpecSensor}, type {type(data)} found")

        dic = super().to_dict(data, version=version)
        dic["central_wavelength"] = data.get_central_wavelength()

        return dic

    def parse_central_wavelength(self, central_wavelength, version=None):
        return "central_wavelength", central_wavelength


ParserManager.register(MSpecSensor, Parser.version, Parser())
