import warnings

from ..image_metadata import ImageMetadata
from ...interface.sensor_interface import ISensor
from ...metadata import Metadata
from ...utils import is_equivalent_to_a_list


class RGBMetadata(ImageMetadata):
    """
    Equivalent to ImageMetadata but containing only elements (among other sensors and images) relating to RGB images.
    """

    @classmethod
    def from_metadata(cls, metadata, show_warnings=True):
        """
        Create an RGBMetadata instance from an existing Metadata instance.

        :param metadata: Metadata instance to base on
        :type metadata: Metadata
        :param show_warnings: indicates whether to display or hide warnings
        :type show_warnings: bool
        :return: RGBMetadata instance from an existing Metadata instance
        :rtype: RGBMetadata

        :note: If the Metadata instance has other sensors and/or data that are not cameras and/or images, these will be
               ignored and a warning will be thrown if show_warning is True.
        """
        return super().from_metadata(metadata, show_warnings)

    def set_sensors(self, sensors, warn_only=True, show_warnings=True):
        """
        Set the list of sensors used for the measurement session.
        Only sensors of type "lidar" will be accepted in the ImageMetadata class context.

        :param sensors: list of sensors used for the measurement session
        :type sensors: list[ISensor]
        :param warn_only: indicates whether an error is simply returned as a warning (especially when a sensor is not a camera)
        :type warn_only: bool
        :param show_warnings: indicates whether to display or hide warnings, useless if warn_only is False
        :type show_warnings: bool
        """
        if not is_equivalent_to_a_list(sensors):
            raise TypeError(f"Argument 'sensors' must be of type {list} (or equivalent), "
                            f"type {type(sensors)} found")
        if not all(isinstance(sensor, ISensor) for sensor in sensors):
            raise TypeError(f"Elements of the 'sensors' argument must be of type {ISensor}, "
                            f"at least one element is not of this type")

        camera_sensors = [sensor for sensor in sensors if sensor.get_type() == "camera"]  # avoid 'multispectral_camera'

        if len(camera_sensors) != len(sensors):
            message = (f"{len(sensors)-len(camera_sensors)} of the {len(sensors)} sensors was ignored since it is "
                       f"not of the 'camera' type. The ignored sensor types are: "
                       f"{', '.join(set(sensor.get_type() for sensor in sensors if sensor.get_type() != 'camera'))}")

            if not warn_only:
                raise Exception(message)
            elif show_warnings:
                warnings.warn(message)

        super().set_sensors(camera_sensors)

    def _filter_unwanted_data(self):
        """
        Filters data based on the type of sensor attached to it.

        Must be executed after data<->sensor binding

        :see: _link_data_and_sensors()
        """
        _data = list()
        for data in self.get_data():
            if data.get_sensor() is None:
                warnings.warn(f"The following data was ignored since no sensor could be attached to it: {data.get_name()}")
            elif data.get_sensor().get_type() != "camera":
                warnings.warn(f"The following data was ignored since the attached sensor is not of type 'camera': {data.get_name()}")
            else: # data.get_sensor() is not None and data.get_sensor().get_type() == "camera"
                _data.append(data)
        self.set_data(_data)

    def _link_data_and_plots(self):
        """
        Private methods for defining connections between Data and Plot.

        Once executed, on a given data `my_data`, the method `my_data.get_plot()` will return the plot (instance) concerned by this data.
        Conversely, a `my_plot` plot will return the list of data concerning it with the `my_plot.get_data()` method.

        :note: This method overrides the parent class method to filter out unwanted data (before being bound to plots).
        """
        self._filter_unwanted_data()  # to filter 'multispectral_camera'
        super()._link_data_and_plots()

    def extend(self, metadata):
        """
        Extends the current RGBMetadata by merging the second RGBMetadata object provided.

        The only thing that will be checked is that the second object is of type RGBMetadata and that their Session and Vector values match.

        :param metadata: another RGBMetadata object
        :type metadata: RGBMetadata

        :warning: Merging is done in-place, so any errors raised may result in corruption of the original metadata. It is therefore not recommended to use this method in a try-catch statement.
        """
        if not isinstance(metadata, RGBMetadata):
            raise TypeError(f"Argument 'metadata' must be of type {RGBMetadata}, "
                            f"type {type(metadata)} found")
        super().extend(metadata)


def to_RGBMetadata(self, show_warnings=True):
    """
    Cast Metadata to RGBMetadata.

    :param self: Metadata instance
    :type self: Metadata
    :param show_warnings: indicates whether to display or hide warnings
    :type show_warnings: bool
    :return: RGBMetadata instance from the current Metadata instance (self)
    :rtype: RGBMetadata

    :see: RGBMetadata.from_metadata()
    """
    return RGBMetadata.from_metadata(self, show_warnings)


setattr(Metadata, "to_RGBMetadata", to_RGBMetadata)
