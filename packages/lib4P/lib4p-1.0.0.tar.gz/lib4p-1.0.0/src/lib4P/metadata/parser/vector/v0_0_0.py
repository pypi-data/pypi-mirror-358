from .. import parser_manager as ParserManager
from ..parser_interface import ParserInterface
from ... import Vector
from ...interface.vector_interface import IVector


class Parser(ParserInterface):

    version = (0, 0, 0)

    def __init__(self):
        self.sub_parsers = {
            "id": self.parse_id,
            "uri": self.parse_uri,
            "serial_nb": self.parse_serial_number,
            "acquisition_version": self.parse_acquisition_version,
            "format_version": self.parse_format_version
        }

    def from_dict(self, data, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs = dict()
        for key in data:
            if key not in self.sub_parsers:
                raise KeyError(f"Unexpected '{key}' key during vector parsing")
            sub_parser = self.sub_parsers.get(key)
            attr, value = sub_parser(data[key], version=version)
            kwargs[attr] = value

        return kwargs

    def to_dict(self, data, version=None):
        if not isinstance(data, IVector):
            raise TypeError(f"Argument 'data' must be of type {IVector}, type {type(data)} found")

        _additional_attributes = data.get_additional_attributes()

        return {
            **_additional_attributes,
            "id": data.get_id(),
            "uri": data.get_uri(),
            "serial_nb": data.get_serial_number()
        }

    def parse_id(self, id, version=None):
        return "id", id

    def parse_uri(self, uri, version=None):
        return "uri", uri

    def parse_serial_number(self, serial_number, version=None):
        return "serial_number", serial_number

    def parse_acquisition_version(self, acquisition_version, version=None):
        return "acquisition_version", acquisition_version

    def parse_format_version(self, format_version, version=None):
        return "format_version", format_version


ParserManager.register("vector", Parser.version, Parser())
ParserManager.register(IVector, Parser.version, Parser())
ParserManager.register(Vector, Parser.version, Parser())
