from .v0_0_0 import Parser as PreviousParser
from .. import parser_manager as ParserManager
from ... import Sensor
from ...interface.sensor_interface import ISensor


class Parser(PreviousParser):  # ParserInterface already inherits from PreviousParser

    version = (1, 0, 0)

    def __init__(self):
        PreviousParser.__init__(self)

        del self.sub_parsers["images"]

    def to_dict(self, data, version=None):
        if not isinstance(data, ISensor):
            raise TypeError(f"Argument 'data' must be of type {ISensor}, type {type(data)} found")

        _position = data.get_position()
        _additional_attributes = data.get_additional_attributes()

        return {
            **{key: value for key, value in _additional_attributes.items()},
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
            }
        }


ParserManager.register("sensor", Parser.version, Parser())
ParserManager.register(ISensor, Parser.version, Parser())
ParserManager.register(Sensor, Parser.version, Parser())
