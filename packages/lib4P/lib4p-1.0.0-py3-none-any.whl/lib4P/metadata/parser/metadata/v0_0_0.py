from .. import parser_manager as ParserManager
from ..parser_interface import ParserInterface
from ...data import Data
from ...geolocation import Geolocation
from ...interface.metadata_interface import IMetadata
from ...plot import Plot
from ...sensor import Sensor
from ...session import Session
from ...vector import Vector


class Parser(ParserInterface):

    version = (0, 0, 0)

    def __init__(self):
        self.sub_parsers = {
            "session": self.parse_session,
            "plot": self.parse_plots,
            "vector": self.parse_vector,
            "geolocalisation": self.parse_geolocations,
            "sensors": self.parse_sensors,
            "static_transforms": self.parse_static_transforms
        }

    def from_dict(self, data, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs = dict()
        for key in data:
            if key not in self.sub_parsers:
                raise KeyError(f"Unexpected '{key}' key during metadata parsing")
            sub_parser = self.sub_parsers.get(key)
            sub_parser(data[key], kwargs, version=version)

        # Pré-linkage plot_id <-> {image, geolocation} à partir des informations sous la main
        plot_id = kwargs["plots"][0].get_id()
        for _data in kwargs["data"]:
            _data.set_additional_attributes({"plot_id": plot_id, **_data.get_additional_attributes()})
        for geolocation in kwargs["geolocations"]:
            geolocation.set_additional_attributes({"plot_id": plot_id, **geolocation.get_additional_attributes()})

        return kwargs

    def to_dict(self, data, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        if not isinstance(data, IMetadata):
            raise TypeError(f"Argument 'data' must be of type {IMetadata}, type {type(data)} found")

        if len(data.get_plots()) > 1:
            raise ValueError(f"For metadata v0.0.0, can only serialize when only one plot is present, "
                             f"{len(data.get_plots())} plots present")

        if len(data.get_geolocations()) > 1:
            raise ValueError(f"For metadata v0.0.0, can only serialize when only one geolocation is present, "
                             f"{len(data.get_geolocations())} geolocations present")

        return {
            # "metadata_version": ".".join(str(v) for v in data._get_version()),  # Not in v0.0.0
            "session": ParserManager.get_parser(type(data.get_session()), version).to_dict(data.get_session(), version=version),
            "plot": ParserManager.get_parser(type(data.get_plot()), version).to_dict(data.get_plot(), version=version),
            "vector": ParserManager.get_parser(type(data.get_vector()), version).to_dict(data.get_vector(), version=version),
            "geolocalisation": ParserManager.get_parser(type(data.get_geolocation()), version).to_dict(data.get_geolocation(), version=version),
            "sensors": [ParserManager.get_parser(type(sensor), version).to_dict(sensor, version=version) for sensor in data.get_sensors()],
            "static_transforms": ParserManager.get_parser("static_transforms", version).to_dict(data.get_static_transforms(), version=version)
        }

    def parse_session(self, data, kwargs, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs["session"] = Session(**ParserManager.get_parser("session", version).from_dict(data, version=version))

    def parse_plots(self, data, kwargs, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        # In this version, the metadata only has one plot entered, so we systematically convert it into a list
        kwargs["plots"] = [Plot(**ParserManager.get_parser("plot", version).from_dict(data, version=version))]

    def parse_vector(self, data, kwargs, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs["vector"] = Vector(**ParserManager.get_parser("vector", version).from_dict(data, version=version))

    def parse_geolocations(self, data, kwargs, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        # In this version, the metadata only has one geolocation entered, so we systematically convert it into a list
        kwargs["geolocations"] = [Geolocation(**ParserManager.get_parser("geolocation", version).from_dict(data, version=version))]

    def parse_sensors(self, data, kwargs, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs["sensors"] = []
        kwargs["data"] = []

        for sensor_data in data:
            _sensor_data = sensor_data["images"]
            real_sensor_data = {key: value for key, value in sensor_data.items() if key != "images"}

            sensor = Sensor(**ParserManager.get_parser("sensor", version).from_dict(real_sensor_data, version=version))
            kwargs["sensors"].append(sensor)

            for _data in _sensor_data:
                args = ParserManager.get_parser("data", version).from_dict(_data, version=version)
                args["sensor_id"] = sensor.get_id()
                if "filename" not in args:
                    args["filename"] = self._get_data_filename(kwargs["vector"], kwargs["plots"][0], args["name"])
                kwargs["data"].append(Data(**args))

    def parse_static_transforms(self, data, kwargs, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs["static_transforms"] = ParserManager.get_parser("static_transforms", version).from_dict(data, version=version)

    def _get_data_filename(self, vector, plot, data_name):
        is_phenomobile = (
            "pheno" in vector.get_id().lower()
            or
            "pheno" in vector.get_serial_number().lower()
        )

        is_camera = ("camera" in data_name)
        is_lidar = (
            "lms" in data_name
            or
            "lidar" in data_name
        )

        if is_camera:
            return "uplot_" + plot.get_id() + "_" + data_name + "_" + ("RGB_WB.tif" if is_phenomobile else "RGB.jpg")
        elif is_lidar:
            return "uplot_" + plot.get_id() + "_" + data_name[:-8] + "_point_cloud.las"  # data_name[:8] removes "_LID.csv" suffix  # TODO : Quid des "*_pos.las" !?


ParserManager.register("metadata", Parser.version, Parser())
ParserManager.register(IMetadata, Parser.version, Parser())
