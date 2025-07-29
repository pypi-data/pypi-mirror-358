from ..interface.sensor_interface import ISensor
from ..interface.sensor_linker_interface import ISensorLinker


class AbstractSensorLinker(ISensorLinker):
    """
    Abstract class defining various functions useful for binding a sensor instance to another object instance.
    """

    def __init__(self):
        super().__init__()
        self._sensor = None

    def link_sensor(self, sensor):
        """
        Links a sensor to the current instance.

        Only one sensor can be linked.

        :param sensor: sensor to link
        :type sensor: Sensor
        """
        if not isinstance(sensor, ISensor):
            raise TypeError(f"Argument 'sensor' must be of type {ISensor}, "
                            f"type {type(sensor)} found")
        self._sensor = sensor

    def has_sensor(self):
        """
        Returns True if a sensor is linked to the current instance.

        :return: True if a sensor is linked to the current instance
        :rtype: bool
        """
        return self._sensor is not None

    def get_sensor(self):
        """
        Returns the sensor linked to the current instance (None if not linked).

        :return: sensor linked to the current instance (None if not linked)
        :rtype: Sensor or None
        """
        return self._sensor
