from .. import parser_manager as ParserManager
from ..parser_interface import ParserInterface
from ... import Sensor
from ...interface.sensor_interface import ISensor
from ...position import Position


class Parser(ParserInterface):

    version = (0, 0, 0)

    def __init__(self):
        self.sub_parsers = {
            "id": self.parse_id,
            "type": self.parse_type,
            "description": self.parse_description,
            "uri": self.parse_uri,
            "serial_nb": self.parse_serial_number,
            "manufacturer": self.parse_manufacturer,
            "position": self.parse_position,
            "images": self.parse_images
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
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        if not isinstance(data, ISensor):
            raise TypeError(f"Argument 'data' must be of type {ISensor}, type {type(data)} found")

        _position = data.get_position()
        _additional_attributes = data.get_additional_attributes()
        _excluded_attributes = ["images"]  # Processing 'images' later
        # Serialization of images via their instances attached to the sensor rather than by the additional attributes
        # originally read.
        # Otherwise, the risk mainly arises when creating a metadata instance from scratch (in which these additional
        # attributes would surely not be specified)

        return {
            **{key: value for key, value in _additional_attributes.items() if key not in _excluded_attributes},
            "id": data.get_id(),
            "type": data.get_type(),
            "description": data.get_description(),
            "uri": data.get_uri(),
            "serial_nb": data.get_serial_number(),
            "manufacturer": data.get_manufacturer(),
            "position": {
                "x": _position.get_x(),
                "y": _position.get_y(),
                "z": _position.get_z(),
                "pitch": _position.get_pitch(),
                "roll": _position.get_roll(),
                "yaw": _position.get_yaw()
            },
            "images": [ParserManager.get_parser(type(image), version=version).to_dict(image) for image in data.get_data()]
        }

    def parse_id(self, id, version=None):
        return "id", id

    def parse_type(self, type, version=None):
        return "type", type

    def parse_description(self, description, version=None):
        return "description", description

    def parse_uri(self, uri, version=None):
        return "uri", uri

    def parse_serial_number(self, serial_number, version=None):
        return "serial_number", serial_number

    def parse_manufacturer(self, manufacturer, version=None):
        return "manufacturer", manufacturer

    def parse_position(self, position, version=None):
        if "x" not in position:
            raise ValueError("Missing 'x' key in 'position' argument during sensor parsing")
        if "y" not in position:
            raise ValueError("Missing 'y' key in 'position' argument during sensor parsing")
        if "z" not in position:
            raise ValueError("Missing 'z' key in 'position' argument during sensor parsing")
        if "yaw" not in position:
            raise ValueError("Missing 'yaw' key in 'position' argument during sensor parsing")
        if "pitch" not in position:
            raise ValueError("Missing 'pitch' key in 'position' argument during sensor parsing")
        if "roll" not in position:
            raise ValueError("Missing 'roll' key in 'position' argument during sensor parsing")

        return "position", Position(position["x"], position["y"], position["z"],
                                    position["yaw"], position["pitch"], position["roll"])

    def parse_images(self, images, version=None):
        return None, None  # Should not be present in the "sensor" key

    def parse_additional_attribute(self, key, attribute, version=None):
        return key, attribute


ParserManager.register("sensor", Parser.version, Parser())
ParserManager.register(ISensor, Parser.version, Parser())
ParserManager.register(Sensor, Parser.version, Parser())
