from .....parser import parser_manager as ParserManager
from .....parser.sensor.v0_0_0 import Parser as BaseParser
from ...camera_sensor import CameraSensor


class Parser(BaseParser):

    def __init__(self):
        BaseParser.__init__(self)

        self.sub_parsers["focal_length"] = self.parse_focal_length
        self.sub_parsers["pixel_size"] = self.parse_pixel_size
        self.sub_parsers["height"] = self.parse_height
        self.sub_parsers["width"] = self.parse_width

    def to_dict(self, data, version=None):
        if not isinstance(data, CameraSensor):
            raise TypeError(f"Argument 'data' must be of type {CameraSensor}, type {type(data)} found")

        dic = super().to_dict(data, version=version)
        dic["focal_length"] = data.get_focal_length()
        dic["pixel_size"] = data.get_pixel_size()
        dic["height"] = data.get_height()
        dic["width"] = data.get_width()

        return dic

    def parse_focal_length(self, focal_length, version=None):
        return "focal_length", focal_length

    def parse_height(self, height, version=None):
        return "height", height

    def parse_width(self, width, version=None):
        return "width", width

    def parse_pixel_size(self, pixel_size, version=None):
        return "pixel_size", pixel_size


ParserManager.register(CameraSensor, Parser.version, Parser())
