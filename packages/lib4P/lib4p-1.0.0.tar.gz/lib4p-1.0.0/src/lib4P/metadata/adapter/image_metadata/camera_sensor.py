from ... import Sensor


class CameraSensor(Sensor):

    def __init__(self, id, type, description, uri, serial_number, manufacturer,
                 focal_length, pixel_size, height, width,
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
        :param focal_length: focal length in millimeters
        :type focal_length: int | float
        :param pixel_size: physical size of a sensor pixel in nanometers
        :type pixel_size: int | float
        :param height: height sensor resolution (i.e. number of pixels over height)
        :type height: int
        :param width: width sensor resolution (i.e. number of pixels over width)
        :type width: int
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
        super().__init__(
            id=id, type=type, description=description, uri=uri, serial_number=serial_number, manufacturer=manufacturer,
            position=position, x=x, y=y, z=z, yaw=yaw, pitch=pitch, roll=roll
        )

        self._focal_length = None
        self.set_focal_length(focal_length)

        self._pixel_size = None
        self.set_pixel_size(pixel_size)

        self._height = None
        self.set_height(height)

        self._width = None
        self.set_width(width)

        self.set_additional_attributes(kwargs)

    @classmethod
    def from_sensor(cls, sensor):
        """
        CameraSensor constructor from ISensor object.

        :param sensor: ISensor object from which to initialize CameraSensor (Sensor specialization)
        :type sensor: ISensor
        :return: Image
        """
        if not isinstance(sensor, Sensor):
            raise TypeError(f"Argument 'sensor' must be of type {Sensor}, type {type(sensor)} found")

        kwargs = sensor.get_additional_attributes()
        _position = sensor.get_position()
        kwargs.update({
            "id": sensor.get_id(), "type": sensor.get_type(), "description": sensor.get_description(),
            "uri": sensor.get_uri(), "serial_number": sensor.get_serial_number(),
            "manufacturer": sensor.get_manufacturer(), "x": _position.get_x(), "y": _position.get_y(),
            "z": _position.get_z(), "yaw": _position.get_yaw(), "pitch": _position.get_pitch(),
            "roll": _position.get_roll()
        })

        try:
            sensor_instance = cls(**kwargs)
        except Exception as e:
            raise Exception("An error occurred while instantiating CameraSensor from a Sensor object. "
                            "This may mean that the provided Sensor object is not compatible with the CameraSensor "
                            "class or that some data is missing to cast the object. "
                            f"The following message was returned: {e.__repr__()}")

        return sensor_instance

    def __eq__(self, other):
        """
        Tests for equality between two `CameraSensor` objects.
        Equality is true when both objects are of type `CameraSensor`, and their `id`, `type`, `description`, `uri`, `serial_number`, `manufacturer`, `focal_length`, `pixel_size`, `height`, `width` and `position` values are equal to each other.

        :param other: another `CameraSensor` object
        :type other: CameraSensor
        :return: true if the two objects are equal
        :rtype: bool
        """
        return (
            isinstance(other, CameraSensor)
            and self.get_focal_length() == other.get_focal_length()
            and self.get_pixel_size() == other.get_pixel_size()
            and self.get_height() == other.get_height()
            and self.get_width() == other.get_width()
            and super().__eq__(other)
        )

    def set_focal_length(self, focal_length):
        """
        Set the focal length (in millimeters).

        :param focal_length: focal length in millimeters
        :type focal_length: int | float
        """
        if not isinstance(focal_length, (int, float)):
            raise TypeError(f"Argument 'focal_length' must be of type {int} or {float}, type {type(focal_length)} found")
        if focal_length <= 0:
            raise ValueError(f"Argument 'focal_length' must be strictly greater than 0, {focal_length} found")
        self._focal_length = focal_length

    def get_focal_length(self):
        """
        Returns the focal length (in millimeters).

        :return: focal length (in millimeters)
        :rtype: int | float
        """
        return self._focal_length

    def set_pixel_size(self, pixel_size):
        """
        Set the physical size of a sensor pixel (in nanometers).

        :param pixel_size: physical size of a sensor pixel (in nanometers)
        :type pixel_size: int | float
        """
        if not isinstance(pixel_size, (int, float)):
            raise TypeError(f"Argument 'pixel_size' must be of type {int} or {float}, type {type(pixel_size)} found")
        if pixel_size <= 0:
            raise ValueError(f"Argument 'pixel_size' must be strictly greater than 0, {pixel_size} found")
        self._pixel_size = pixel_size

    def get_pixel_size(self):
        """
        Returns the physical size of a sensor pixel (in nanometers).

        :return: physical size of a sensor pixel (in nanometers)
        :rtype: int | float
        """
        return self._pixel_size

    def set_height(self, height):
        """
        Set the height sensor resolution (i.e. number of pixels over height).

        :param height: height sensor resolution (i.e. number of pixels over height)
        :type height: int | float

        :note: Float type added for backwards compatibility.
        """
        if not isinstance(height, (int, float)):
            raise TypeError(f"Argument 'height' must be of type {int}, type {type(height)} found")
        if height <= 0:
            raise ValueError(f"Argument 'height' must be strictly greater than 0, {height} found")
        self._height = height

    def get_height(self):
        """
        Returns the height sensor resolution (i.e. number of pixels over height).

        :return: height sensor resolution (i.e. number of pixels over height)
        :rtype: int
        """
        return self._height

    def set_width(self, width):
        """
        Set the width sensor resolution (i.e. number of pixels over width).

        :param width: width sensor resolution (i.e. number of pixels over width)
        :type width: int | float

        :note: Float type added for backwards compatibility.
        """
        if not isinstance(width, (int, float)):
            raise TypeError(f"Argument 'width' must be of type {int}, type {type(width)} found")
        if width <= 0:
            raise ValueError(f"Argument 'width' must be strictly greater than 0, {width} found")
        self._width = width

    def get_width(self):
        """
        Returns the width sensor resolution (i.e. number of pixels over width).

        :return: width sensor resolution (i.e. number of pixels over width)
        :rtype: int
        """
        return self._width
