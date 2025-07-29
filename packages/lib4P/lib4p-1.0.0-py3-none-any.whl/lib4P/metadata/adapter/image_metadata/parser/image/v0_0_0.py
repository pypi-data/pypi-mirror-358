from .....parser import parser_manager as ParserManager
from .....parser.data.v0_0_0 import Parser as BaseParser
from ...image import Image


class Parser(BaseParser):

    def __init__(self):
        BaseParser.__init__(self)

        self.sub_parsers["shutter_time"] = self.parse_shutter_time
        self.sub_parsers["height"] = self.parse_height
        self.sub_parsers["width"] = self.parse_width
        self.sub_parsers["size"] = self.parse_size

    def to_dict(self, data, version=None):
        if not isinstance(data, Image):
            raise TypeError(f"Argument 'data' must be of type {Image}, type {type(data)} found")

        dic = super().to_dict(data, version=version)
        dic["shutter_time"] = data.get_shutter_time()
        dic["height"] = data.get_height()
        dic["width"] = data.get_width()
        dic["size"] = data.get_size()

        return dic

    def parse_shutter_time(self, shutter_time, version=None):
        return "shutter_time", shutter_time

    def parse_height(self, height, version=None):
        return "height", height

    def parse_width(self, width, version=None):
        return "width", width

    def parse_size(self, size, version=None):
        return "size", size


ParserManager.register("image", Parser.version, Parser())
ParserManager.register(Image, Parser.version, Parser())
