from .. import parser_manager as ParserManager
from ..parser_interface import ParserInterface


class Parser(ParserInterface):

    version = (0, 0, 0)

    def from_dict(self, data, version=None):
        return data

    def to_dict(self, data, version=None):
        return data


ParserManager.register("static_transforms", Parser.version, Parser())
