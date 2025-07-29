from .. import parser_manager as ParserManager
from ..parser_interface import ParserInterface
from ... import Plot
from ...interface.plot_interface import IPlot


class Parser(ParserInterface):

    version = (0, 0, 0)

    def __init__(self):
        self.sub_parsers = {
            "id": self.parse_id,
            "uri": self.parse_uri,
            "coordinates": self.parse_coordinates,
            "orientation": self.parse_orientation
        }

    def from_dict(self, data, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs = dict()
        for key in data:
            if key not in self.sub_parsers:
                attr, value = self.parse_additional_attribute(key, data[key], version=version)
            else:
                sub_parser = self.sub_parsers.get(key)
                attr, value = sub_parser(data[key], version=version)

            if attr is not None:
                kwargs[attr] = value

        return kwargs

    def to_dict(self, data, version=None):
        if not isinstance(data, IPlot):
            raise TypeError(f"Argument 'data' must be of type {IPlot}, type {type(data)} found")

        _additional_attributes = data.get_additional_attributes()

        return {
            **{key: value for key, value in _additional_attributes.items()},
            "id": data.get_id(),
            "uri": data.get_uri(),
            "coordinates": data.get_coordinates(),
            "orientation": data.get_orientation()
        }

    def parse_id(self, id, version=None):
        # In the case where the id would have been interpreted as a numeric value, we force the conversion to str
        if isinstance(id, int):
            id = str(id)
        return "id", id

    def parse_uri(self, uri, version=None):
        return "uri", uri

    def parse_coordinates(self, coordinates, version=None):
        return "coordinates", coordinates

    def parse_orientation(self, orientation, version=None):
        return "orientation", orientation

    def parse_additional_attribute(self, key, attribute, version=None):
        return key, attribute


ParserManager.register("plot", Parser.version, Parser())
ParserManager.register(IPlot, Parser.version, Parser())
ParserManager.register(Plot, Parser.version, Parser())
