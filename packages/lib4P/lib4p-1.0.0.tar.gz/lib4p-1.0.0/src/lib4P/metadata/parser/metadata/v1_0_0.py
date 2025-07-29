from .v0_0_0 import Parser as PreviousParser
from .. import parser_manager as ParserManager
from ...data import Data
from ...geolocation import Geolocation
from ...interface.metadata_interface import IMetadata
from ...plot import Plot
from ...sensor import Sensor


class Parser(PreviousParser):  # ParserInterface already inherits from PreviousParser

    version = (1, 0, 0)

    def __init__(self):
        PreviousParser.__init__(self)

        del self.sub_parsers["plot"]
        del self.sub_parsers["geolocalisation"]

        self.sub_parsers["metadata_version"] = self.parse_version
        self.sub_parsers["session"] = self.parse_session
        self.sub_parsers["plots"] = self.parse_plots
        self.sub_parsers["geolocations"] = self.parse_geolocations
        self.sub_parsers["sensors"] = self.parse_sensors
        self.sub_parsers["data"] = self.parse_data

    def from_dict(self, data, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs = dict()
        for key in data:
            if key not in self.sub_parsers:
                raise KeyError(f"Unexpected '{key}' key during metadata parsing")
            sub_parser = self.sub_parsers.get(key)
            sub_parser(data[key], kwargs, version=version)

        return kwargs

    def to_dict(self, data, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        if not isinstance(data, IMetadata):
            raise TypeError(f"Argument 'data' must be of type {IMetadata}, type {type(data)} found")

        return {
            "metadata_version": ".".join(str(v) for v in version),#".".join(str(v) for v in data._get_version()),
            "session": ParserManager.get_parser(type(data.get_session()), version).to_dict(data.get_session(), version=version),
            "plots": [ParserManager.get_parser(type(plot), version).to_dict(plot, version=version) for plot in data.get_plots()],
            "vector": ParserManager.get_parser(type(data.get_vector()), version).to_dict(data.get_vector(), version=version),
            "geolocations": [ParserManager.get_parser(type(geolocation), version).to_dict(geolocation, version=version) for geolocation in data.get_geolocations()],
            "sensors": [ParserManager.get_parser(type(sensor), version).to_dict(sensor, version=version) for sensor in data.get_sensors()],
            "data": [ParserManager.get_parser(type(_data), version).to_dict(_data, version=version) for _data in data.get_data()],
            "static_transforms": ParserManager.get_parser("static_transforms", version).to_dict(data.get_static_transforms(), version=version)
        }

    def parse_plots(self, data, kwargs, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs["plots"] = [Plot(**ParserManager.get_parser("plot", version).from_dict(plot_data, version=version)) for plot_data in data]

    def parse_geolocations(self, data, kwargs, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs["geolocations"] = [Geolocation(**ParserManager.get_parser("geolocation", version).from_dict(geolocation_data, version=version)) for geolocation_data in data]

    def parse_sensors(self, data, kwargs, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs["sensors"] = [Sensor(**ParserManager.get_parser("sensor", version).from_dict(sensor_data, version=version)) for sensor_data in data]

    def parse_data(self, data, kwargs, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs["data"] = [Data(**ParserManager.get_parser("data", version).from_dict(_data, version=version)) for _data in data]

    def parse_version(self, data, kwargs, version=None):
        kwargs["version"] = data


ParserManager.register("metadata", Parser.version, Parser())
ParserManager.register(IMetadata, Parser.version, Parser())
