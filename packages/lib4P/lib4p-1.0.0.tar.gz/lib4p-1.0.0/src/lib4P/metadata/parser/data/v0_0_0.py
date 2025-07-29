from .. import parser_manager as ParserManager
from ..parser_interface import ParserInterface
from ... import Data
from ...interface.data_interface import IData


class Parser(ParserInterface):

    version = (0, 0, 0)

    def __init__(self):
        self.sub_parsers = {
            "filename": self.parse_filename,
            "name": self.parse_name,
            "date": self.parse_date
        }

    def from_dict(self, data, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs = dict()
        for key in data:
            if key not in self.sub_parsers:
                # raise KeyError(f"Unexpected '{key}' key during image parsing")
                attr, value = self.parse_additional_attribute(key, data[key], version=version)
            else:
                sub_parser = self.sub_parsers.get(key)
                attr, value = sub_parser(data[key], version=version)

            if attr is not None:
                kwargs[attr] = value

        return kwargs

    def to_dict(self, data, version=None):
        if not isinstance(data, IData):
            raise TypeError(f"Argument 'data' must be of type {IData}, type {type(data)} found")

        _additional_attributes = data.get_additional_attributes()

        return {
            **_additional_attributes,
            "name": data.get_name(),
            "date": data.get_date().strftime("%Y-%m-%d_%H:%M:%S.%f")
        }

    def parse_filename(self, filename, version=None):
        return "filename", filename

    def parse_name(self, name, version=None):
        return "name", name

    def parse_date(self, date, version=None):
        return "date", date

    def parse_additional_attribute(self, key, attribute, version=None):
        return key, attribute


ParserManager.register("data", Parser.version, Parser())
ParserManager.register(IData, Parser.version, Parser())
ParserManager.register(Data, Parser.version, Parser())
