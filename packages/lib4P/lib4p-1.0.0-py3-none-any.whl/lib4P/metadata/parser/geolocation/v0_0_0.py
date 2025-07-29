from .. import parser_manager as ParserManager
from ..parser_interface import ParserInterface
from ... import Geolocation
from ...interface.geolocation_interface import IGeolocation


class Parser(ParserInterface):

    version = (0, 0, 0)

    def __init__(self):
        self.sub_parsers = {
            "filename": self.parse_filename
        }

    def from_dict(self, data, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs = dict()
        for key in data:
            if key not in self.sub_parsers:
                raise KeyError(f"Unexpected '{key}' key during geolocation parsing")
            sub_parser = self.sub_parsers.get(key)
            attr, value = sub_parser(data[key], version=version)
            kwargs[attr] = value

        return kwargs

    def to_dict(self, data, version=None):
        if not isinstance(data, IGeolocation):
            raise TypeError(f"Argument 'data' must be of type {IGeolocation}, type {type(data)} found")

        return {
            "filename": data.get_filename()
        }

    def parse_filename(self, filename, version=None):
        return "filename", filename


ParserManager.register("geolocation", Parser.version, Parser())
ParserManager.register(IGeolocation, Parser.version, Parser())
ParserManager.register(Geolocation, Parser.version, Parser())
