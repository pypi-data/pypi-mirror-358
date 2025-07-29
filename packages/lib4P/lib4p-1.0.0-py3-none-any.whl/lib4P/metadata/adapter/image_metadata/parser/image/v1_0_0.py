from .v0_0_0 import Parser as PreviousParser
from ...image import Image
from .....parser import parser_manager as ParserManager
from .....parser.data.v1_0_0 import Parser as BaseDataParser


class Parser(PreviousParser, BaseDataParser):

    def __init__(self):
        PreviousParser.__init__(self)
        BaseDataParser.__init__(self)

    def to_dict(self, data, version=None):
        if not isinstance(data, Image):
            raise TypeError(f"Argument 'data' must be of type {Image}, type {type(data)} found")

        dic = super().to_dict(data, version=version)

        return dic


ParserManager.register("image", Parser.version, Parser())
ParserManager.register(Image, Parser.version, Parser())
