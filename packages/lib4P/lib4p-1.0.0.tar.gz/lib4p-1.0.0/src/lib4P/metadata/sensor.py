import builtins

from .abstract.abstract_additional_attributes import AbstractAdditionalAttributes
from .abstract.abstract_data_linker import AbstractDataLinker
from .abstract.abstract_metadata_linker import AbstractMetadataLinker
from .interface.sensor_interface import ISensor
from .position import Position


class Sensor(ISensor, AbstractMetadataLinker, AbstractDataLinker, AbstractAdditionalAttributes):

    def __init__(self, id, type, description, uri, serial_number, manufacturer,
                 *,  # to force explicit use of argument names
                 position=None, x=None, y=None, z=None, yaw=None, pitch=None, roll=None,
                 **kwargs):
        """
        Sensor used for the measurement session.

        :param id: sensor identifier
        :type id: str
        :param type: type of sensor (e.g. camera, lidar, etc.)
        :type type: str
        :param description: description of the sensor, usually used to name the sensor
        :type description: str
        :param uri: URI associated with the sensor for the PHIS platform
        :type uri: str
        :param serial_number: sensor serial number
        :type serial_number: str
        :param manufacturer: sensor manufacturer
        :type manufacturer: str
        :param position: position of the sensor relative to the vector
        :type position: Position
        :param x: x coordinate of the sensor relative to the vector, not used if `position` is specified
        :type x: int or float
        :param y: y coordinate of the sensor relative to the vector, not used if `position` is specified
        :type y: int or float
        :param z: z coordinate of the sensor relative to the vector, not used if `position` is specified
        :type z: int or float
        :param yaw: yaw angle of the sensor relative to the vector, not used if `position` is specified
        :type yaw: int or float
        :param pitch: pitch angle of the sensor relative to the vector, not used if `position` is specified
        :type pitch: int or float
        :param roll: roll angle of the sensor relative to the vector, not used if `position` is specified
        :type roll: int or float
        :param kwargs: additional attributes linked to the sensor (e.g. sensor dimension, focal length, etc.)

        :note: You can instantiate the `Sensor` object either by specifying the `position` argument or by specifying the 6 arguments `x`, `y`, `z`, `yaw`, `pitch` and `roll`. In both cases, you must explicitly name the arguments.
        """
        super().__init__()

        self._id = None
        self.set_id(id)

        self._type = None
        self.set_type(type)

        self._description = None
        self.set_description(description)

        self._uri = None
        self.set_uri(uri)

        self._serial_number = None
        self.set_serial_number(serial_number)

        self._manufacturer = None
        self.set_manufacturer(manufacturer)

        if position is None:
            position = Position(x, y, z, yaw, pitch, roll)
        self._position = None
        self.set_position(position)

        self.set_additional_attributes(kwargs)

    def __eq__(self, other):
        """
        Tests for equality between two `Sensor` objects.
        Equality is true when both objects are of type `Sensor`, and their `id`, `type`, `description`, `uri`, `serial_number`, `manufacturer` and `position` values are equal to each other.

        :param other: another `Sensor` object
        :type other: Sensor
        :return: true if the two objects are equal
        :rtype: bool
        """
        return (
                isinstance(other, ISensor)
                and self.get_id() == other.get_id()
                and self.get_type() == other.get_type()
                and self.get_description() == other.get_description()
                and self.get_uri() == other.get_uri()
                and self.get_serial_number() == other.get_serial_number()
                and self.get_manufacturer() == other.get_manufacturer()
                and self.get_position() == other.get_position()
        )

    def set_id(self, id):
        """
        Set the sensor identifier.

        :param id: sensor identifier
        :type id: str
        """
        if not isinstance(id, str):
            raise TypeError(f"Argument 'id' must be of type {str}, type {type(id)} found")
        if id == "":
            raise ValueError("Argument 'id' must not be empty")
        self._id = id

    def get_id(self):
        """
        Returns the sensor identifier.

        :return: sensor identifier
        :rtype: str
        """
        return self._id

    def set_type(self, type):
        """
        Set the type of sensor (e.g. camera, lidar, etc.)

        :param type: type of sensor (e.g. camera, lidar, etc.)
        :type type: str
        """
        if not isinstance(type, str):
            raise TypeError(f"Argument 'type' must be of type {str}, type {builtins.type(type)} found")
        self._type = type

    def get_type(self):
        """
        Returns the type of sensor (e.g. camera, lidar, etc.)

        :return: type of sensor (e.g. camera, lidar, etc.)
        :rtype: str
        """
        return self._type

    def set_description(self, description):
        """
        Set the description of the sensor, usually used to name the sensor.

        :param description: description of the sensor, usually used to name the sensor
        :type description: str
        """
        if not isinstance(description, str):
            raise TypeError(f"Argument 'description' must be of type {str}, type {type(description)} found")
        self._description = description

    def get_description(self):
        """
        Returns the description of the sensor, usually used to name the sensor.

        :return: description of the sensor, usually used to name the sensor
        :rtype: str
        """
        return self._description

    def set_uri(self, uri):
        """
        Set the URI associated with the sensor for the PHIS platform.

        :param uri: URI associated with the sensor for the PHIS platform
        :type uri: str
        """
        if not isinstance(uri, str):
            raise TypeError(f"Argument 'uri' must be of type {str}, type {type(uri)} found")
        self._uri = uri

    def get_uri(self):
        """
        Returns the URI associated with the sensor for the PHIS platform.

        :return: URI associated with the sensor for the PHIS platform
        :rtype: str
        """
        return self._uri

    def set_serial_number(self, serial_number):
        """
        Set the sensor serial number.

        :param serial_number: sensor serial number
        :type serial_number: str
        """
        if not isinstance(serial_number, str):
            raise TypeError(f"Argument 'serial_number' must be of type {str}, type {type(serial_number)} found")
        self._serial_number = serial_number

    def get_serial_number(self):
        """
        Returns the sensor serial number.

        :return: sensor serial number
        :rtype: str
        """
        return self._serial_number

    def set_manufacturer(self, manufacturer):
        """
        Set the sensor manufacturer.

        :param manufacturer: sensor manufacturer
        :type manufacturer: str
        """
        if not isinstance(manufacturer, str):
            raise TypeError(f"Argument 'manufacturer' must be of type {str}, type {type(manufacturer)} found")
        self._manufacturer = manufacturer

    def get_manufacturer(self):
        """
        Returns the sensor manufacturer.

        :return: sensor manufacturer
        :rtype: str
        """
        return self._manufacturer

    def set_position(self, position):
        """
        Set the position of the sensor relative to the vector.

        :param position: position of the sensor relative to the vector
        :type position: Position
        """
        if not isinstance(position, Position):
            raise TypeError(f"Argument 'position' must be of type {Position}, type {type(position)} found")
        self._position = position

    def get_position(self):
        """
        Returns the position of the sensor relative to the vector.

        :return: position of the sensor relative to the vector
        :rtype: Position
        """
        return self._position
