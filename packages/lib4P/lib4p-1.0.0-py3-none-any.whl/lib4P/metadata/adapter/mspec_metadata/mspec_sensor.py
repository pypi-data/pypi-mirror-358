from ..image_metadata.camera_sensor import CameraSensor


class MSpecSensor(CameraSensor):

    def __init__(self, id, type, description, uri, serial_number, manufacturer,
                 focal_length, pixel_size, height, width, central_wavelength,
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
        :param central_wavelength: the central wavelength used by the multispectral sensor (in nm)
        :type central_wavelength: int
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

        :note: You can instantiate the `MSpecSensor` object either by specifying the `position` argument or by specifying the 6 arguments `x`, `y`, `z`, `yaw`, `pitch` and `roll`. In both cases, you must explicitly name the arguments.
        """
        super().__init__(
            id=id, type=type, description=description, uri=uri, serial_number=serial_number, manufacturer=manufacturer,
            focal_length=focal_length, pixel_size=pixel_size, height=height, width=width,
            position=position, x=x, y=y, z=z, yaw=yaw, pitch=pitch, roll=roll
        )

        self._central_wavelength = None
        self.set_central_wavelength(central_wavelength)

        self.set_additional_attributes(kwargs)

    def __eq__(self, other):
        """
        Tests for equality between two `MSpecSensor` objects.
        Equality is true when both objects are of type `MSpecSensor`, and their `id`, `type`, `description`, `uri`, `serial_number`, `manufacturer`, `focal_length`, `pixel_size`, `height`, `width`, `central_wavelength` and `position` values are equal to each other.

        :param other: another `MSpecSensor` object
        :type other: MSpecSensor
        :return: true if the two objects are equal
        :rtype: bool
        """
        return (
            isinstance(other, MSpecSensor)
            and self.get_central_wavelength() == other.get_central_wavelength()
            and super().__eq__(other)
        )

    def set_central_wavelength(self, wavelength):
        """
        Set the (central) wavelength used by the multispectral sensor.
        The wavelength is expressed in nanometers (nm).

        :param wavelength: the central wavelength in nanometers (nm)
        :type wavelength: int
        """
        if not isinstance(wavelength, int):
            raise TypeError(f"Argument 'wavelength' must be of type {int}, type {type(wavelength)} found")
        if wavelength <= 0:
            raise ValueError(f"Argument 'wavelength' must be strictly greater than 0, {wavelength} found")
        self._central_wavelength = wavelength

    def get_central_wavelength(self):
        """
        Returns the (central) wavelength used by the multispectral sensor.
        The wavelength is expressed in nanometers (nm).

        :return: the central wavelength in nanometers (nm)
        :rtype: int
        """
        return self._central_wavelength
