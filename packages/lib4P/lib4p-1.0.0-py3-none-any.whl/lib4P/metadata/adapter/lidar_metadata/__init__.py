import warnings

from ...interface.data_interface import IData
from ...interface.sensor_interface import ISensor
from ...metadata import Metadata
from ...utils import is_equivalent_to_a_list


class LiDARMetadata(Metadata):
    """
    Equivalent to Metadata but containing only elements (among other sensors and data) relating to LiDAR.
    """

    def __init__(self, session, plots, vector, geolocations, sensors, data, static_transforms, version=None, **kwargs):
        """
        Metadata of a measurement session.

        :param session: measurement session information
        :type session: ISession
        :param plots: list of plots concerned by the measurement session
        :type plots: list[IPlot]
        :param vector: vector used for the measurement session
        :type vector: IVector
        :param geolocations: list of geolocations concerned by the measurement session
        :type geolocations: list[IGeolocation]
        :param sensors: list of sensors used for the measurement session
        :type sensors: list[ISensor]
        :param data: list of data acquired by a given sensor during the measurement session
        :type data: list[IData]
        :param static_transforms: [TODO] Not enough information about this argument
        :type static_transforms: Any
        :param version: format version of the metadata, used mainly for serialization/parsing. If None, the version set by default will correspond to the highest parser version.
        :type version: str or tuple
        :param kwargs: additional attributes linked to metadata
        """
        super().__init__(
            session=session, plots=plots, vector=vector, geolocations=geolocations, sensors=sensors, data=data,
            static_transforms=static_transforms, version=version, **kwargs
        )

        # self._filter_unwanted_data()

    @classmethod
    def from_metadata(cls, metadata, show_warnings=True):
        """
        Create an LiDARMetadata instance from an existing Metadata instance.

        :param metadata: Metadata instance to base on
        :type metadata: Metadata
        :param show_warnings: indicates whether to display or hide warnings
        :type show_warnings: bool
        :return: LiDARMetadata instance from an existing Metadata instance
        :rtype: LiDARMetadata

        :note: If the Metadata instance has other sensors and/or data that are not cameras and/or images, these will be
               ignored and a warning will be thrown if show_warning is True.
        """
        if not isinstance(metadata, Metadata):
            raise TypeError(f"Argument 'metadata' must be of type {Metadata}, type {type(metadata)} found")

        with warnings.catch_warnings():
            if not show_warnings:
                warnings.simplefilter("ignore")
            return cls.from_dict(metadata.to_dict())

    def set_sensors(self, sensors, warn_only=True, show_warnings=True):
        """
        Set the list of sensors used for the measurement session.
        Only sensors of type "lidar" will be accepted in the ImageMetadata class context.

        :param sensors: list of sensors used for the measurement session
        :type sensors: list[ISensor]
        :param warn_only: indicates whether an error is simply returned as a warning (especially when a sensor is not a lidar)
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

        lidar_sensors = [sensor for sensor in sensors if sensor.get_type() == "lidar"]

        if len(lidar_sensors) != len(sensors):
            message = (f"{len(sensors)-len(lidar_sensors)} of the {len(sensors)} sensors was ignored since it is "
                       f"not of the 'lidar' type. The ignored sensor types are: "
                       f"{', '.join(set(sensor.get_type() for sensor in sensors if sensor.get_type() != 'lidar'))}")

            if not warn_only:
                raise Exception(message)
            elif show_warnings:
                warnings.warn(message)

        super().set_sensors(lidar_sensors)

    def _filter_unwanted_data(self):
        """
        Filters data based on the type of sensor attached to it.

        Must be executed after data<->sensor binding

        :see: _link_data_and_sensors()
        """
        _data = list()
        for data in self.get_data():
            if data.get_sensor() is not None and data.get_sensor().get_type() == "lidar":
                _data.append(data)
        self.set_data(_data)

    def _link_data_and_plots(self):
        """
        Private methods for defining connections between Data and Plot.

        Once executed, on a given data `my_data`, the method `my_data.get_plot()` will return the plot (instance) concerned by this data.
        Conversely, a `my_plot` plot will return the list of data concerning it with the `my_plot.get_data()` method.

        :note: This method overrides the parent class method to filter out unwanted data (before being bound to plots).
        """
        self._filter_unwanted_data()
        super()._link_data_and_plots()

    def extend(self, metadata):
        """
        Extends the current LiDARMetadata by merging the second LiDARMetadata object provided.

        The only thing that will be checked is that the second object is of type LiDARMetadata and that their Session and Vector values match.

        :param metadata: another LiDARMetadata object
        :type metadata: LiDARMetadata

        :warning: Merging is done in-place, so any errors raised may result in corruption of the original metadata. It is therefore not recommended to use this method in a try-catch statement.
        """
        if not isinstance(metadata, LiDARMetadata):
            raise TypeError(f"Argument 'metadata' must be of type {LiDARMetadata}, "
                            f"type {type(metadata)} found")
        super().extend(metadata)


def to_LiDARMetadata(self, show_warnings=True):
    """
    Cast Metadata to LiDARMetadata.

    :param self: Metadata instance
    :type self: Metadata
    :param show_warnings: indicates whether to display or hide warnings
    :type show_warnings: bool
    :return: LiDARMetadata instance from the current Metadata instance (self)
    :rtype: LiDARMetadata

    :see: LiDARMetadata.from_metadata()
    """
    return LiDARMetadata.from_metadata(self, show_warnings)


setattr(Metadata, "to_LiDARMetadata", to_LiDARMetadata)