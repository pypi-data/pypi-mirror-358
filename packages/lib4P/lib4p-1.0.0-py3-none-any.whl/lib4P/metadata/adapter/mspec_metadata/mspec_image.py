from .mspec_sensor import MSpecSensor
from ..image_metadata.image import Image


class MSpecImage(Image):

    def link_sensor(self, sensor):
        """
        Links a sensor to the current instance.

        Only one sensor can be linked.

        :param sensor: sensor to link
        :type sensor: MSpecSensor
        """
        if not isinstance(sensor, MSpecSensor):
            raise TypeError(f"Argument 'sensor' must be of type {MSpecSensor}, "
                            f"type {type(sensor)} found")

        super().link_sensor(sensor)

    def get_sensor(self):
        """
        Returns the sensor linked to the current instance (None if not linked).

        :return: sensor linked to the current instance (None if not linked)
        :rtype: MSpecSensor or None
        """
        return super().get_sensor()

    def get_central_wavelength(self):
        """
        Returns the central wavelength specific to this image.

        This information is directly retrieved from the linked sensor.

        :return: the central wavelength specific to this image
        :rtype: int or None
        """
        if sensor := self.get_sensor() is not None:
            return sensor.get_central_wavelength()
        return None
