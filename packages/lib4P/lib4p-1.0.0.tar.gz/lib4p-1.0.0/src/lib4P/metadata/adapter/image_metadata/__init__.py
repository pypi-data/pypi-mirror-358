import warnings

from .parser import *
from .camera_sensor import CameraSensor
from .plot import Plot
from ...adapter.image_metadata.image import Image
from ...interface.data_interface import IData
from ...interface.plot_interface import IPlot
from ...interface.sensor_interface import ISensor
from ...metadata import Metadata
from ...utils import is_equivalent_to_a_list


class ImageMetadata(Metadata):
    """
    Equivalent to Metadata but containing only elements (among other sensors and data) relating to images.
    """

    @classmethod
    def from_metadata(cls, metadata, show_warnings=True):
        """
        Create an ImageMetadata instance from an existing Metadata instance.

        :param metadata: Metadata instance to base on
        :type metadata: Metadata
        :param show_warnings: indicates whether to display or hide warnings
        :type show_warnings: bool
        :return: ImageMetadata instance from an existing Metadata instance
        :rtype: ImageMetadata

        :note: If the Metadata instance has other sensors and/or data that are not cameras and/or images, these will be
               ignored and a warning will be thrown if show_warning is True.
        """
        if not isinstance(metadata, Metadata):
            raise TypeError(f"Argument 'metadata' must be of type {Metadata}, type {type(metadata)} found")

        with warnings.catch_warnings():
            if not show_warnings:
                warnings.simplefilter("ignore")
            return cls.from_dict(metadata.to_dict())

    def set_plots(self, plots):
        """
        Set the list of plots concerned by the measurement session.

        :param plots: list of plots concerned by the measurement session
        :type plots: list[IPlot]
        """
        if not is_equivalent_to_a_list(plots):
            raise TypeError(f"Argument 'plots' must be of type {list} (or equivalent), "
                            f"type {type(plots)} found")
        if not all(isinstance(plot, IPlot) for plot in plots):
            raise TypeError(f"Elements of the 'plots' argument must be of type {IPlot}, "
                            f"at least one element is not of this type")
        for plot in plots:
            plot.__class__ = Plot  # Cast to specialized class (only having aliases)

        super().set_plots(plots)

    def get_plots(self):
        """
        Returns the list of plots concerned by the measurement session.

        :return: list of plots concerned by the measurement session
        :rtype: list[Plot]
        """
        return super().get_plots()

    def get_plot(self):
        """
        Returns the plot concerned by the measurement session.
        If multiple plots are present, raises an error.

        :return: the plot concerned by the measurement session
        :rtype: Plot

        :note: This function is only present for convenience in the case where a single plot is processed (saving the user from performing `get_plots()[0]` itself). The preferred way remains to loop over all the plots, without any a priori on their number.
        """
        return super().get_plot()

    def set_sensors(self, sensors, warn_only=True, show_warnings=True):
        """
        Set the list of sensors used for the measurement session.
        Only sensors of type "camera" will be accepted in the ImageMetadata class context.

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

        camera_sensors = [sensor for sensor in sensors if "camera" in sensor.get_type()]

        if len(camera_sensors) != len(sensors):
            message = (f"{len(sensors)-len(camera_sensors)} of the {len(sensors)} sensors was ignored since it is "
                       f"not of the 'camera' type. The ignored sensor types are: "
                       f"{', '.join(set(sensor.get_type() for sensor in sensors if 'camera' not in sensor.get_type()))}")

            if not warn_only:
                raise Exception(message)
            elif show_warnings:
                warnings.warn(message)

        _sensors = list()
        for i in range(len(camera_sensors)):
            if isinstance(camera_sensors[i], CameraSensor):
                _sensors.append(camera_sensors[i])
            elif not warn_only:  # Something else but at least ISensor (according to previous conditions)
                _sensors.append(CameraSensor.from_sensor(camera_sensors[i]))
            else:
                try:
                    _sensors.append(CameraSensor.from_sensor(camera_sensors[i]))
                except Exception as e:
                    if show_warnings:
                        warnings.warn(f"The element with index {i} in the provided 'camera_sensors' encountered the following "
                                      f"error and will not be added to the metadata: {e.__repr__()}")

        super().set_sensors(_sensors)

    def get_sensors(self):
        """
        Returns the list of sensors used for the measurement session.

        :return: list of sensors used for the measurement session
        :rtype: list[CameraSensor]
        """
        return super().get_sensors()

    def set_data(self, data, warn_only=True, show_warnings=True):
        """
        Set the list of data acquired by a given sensor during the measurement session.

        :param data: list of data acquired by a given sensor during the measurement session
        :type data: list[IData]
        :param warn_only: indicates whether an error is simply returned as a warning (especially when a Data is not castable in Image)
        :type warn_only: bool
        :param show_warnings: indicates whether to display or hide warnings, useless if warn_only is False
        :type show_warnings: bool
        """
        if not is_equivalent_to_a_list(data):
            raise TypeError(f"Argument 'data' must be of type {list} (or equivalent), "
                            f"type {type(data)} found")
        if not all(isinstance(_data, IData) for _data in data):
            raise TypeError(f"Elements of the 'data' argument must be of type {IData}, "
                            f"at least one element is not of this type")

        _data = list()
        for i in range(len(data)):
            if isinstance(data[i], Image):
                _data.append(data[i])
            elif not warn_only:  # Something else but at least IData (according to previous conditions)
                _data.append(Image.from_data(data[i]))
            else:
                try:
                    _data.append(Image.from_data(data[i]))
                except Exception as e:
                    if show_warnings:
                        warnings.warn(f"The element with index {i} in the provided 'data' encountered the following "
                                      f"error and will not be added to the metadata: {e.__repr__()}")

        super().set_data(_data)

    def get_data(self):
        """
        Returns the list of data acquired by a given sensor during the measurement session.

        :return: list of data acquired by a given sensor during the measurement session
        :rtype: list[Image]
        """
        return super().get_data()

    def set_images(self, images):
        """
        Alias for method `set_data(self, data)` (see parent class and current class overload).

        :param images: list of images acquired by a given sensor during the measurement session
        :type images: list[IData | Image]

        :note: Data instances will be cast to Image.
        """
        self.set_data(images)

    def get_images(self):
        """
        Alias for method `get_data(self)` (see parent class).

        :return: list of images acquired by a given sensor during the measurement session
        :rtype: list[Image]
        """
        return self.get_data()

    def get_image_from_filename(self, filename):
        """
        Alias for method `get_image_from_filename(self, filename)` (see parent class).

        :param filename: filename searched
        :type filename: str
        :return: Image or None
        """
        return self.get_data_from_filename(filename)

    def extend(self, metadata):
        """
        Extends the current ImageMetadata by merging the second ImageMetadata object provided.
    
        The only thing that will be checked is that the second object is of type ImageMetadata and that their Session and Vector values match.
    
        :param metadata: another ImageMetadata object
        :type metadata: ImageMetadata
    
        :warning: Merging is done in-place, so any errors raised may result in corruption of the original metadata. It is therefore not recommended to use this method in a try-catch statement.
        """
        if not isinstance(metadata, ImageMetadata):
            raise TypeError(f"Argument 'metadata' must be of type {ImageMetadata}, "
                            f"type {type(metadata)} found")
        super().extend(metadata)


def to_ImageMetadata(self, show_warnings=True):
    """
    Cast Metadata to ImageMetadata.

    :param self: Metadata instance
    :type self: Metadata
    :param show_warnings: indicates whether to display or hide warnings
    :type show_warnings: bool
    :return: ImageMetadata instance from the current Metadata instance (self)
    :rtype: ImageMetadata

    :see: ImageMetadata.from_metadata()
    """
    return ImageMetadata.from_metadata(self, show_warnings)


setattr(Metadata, "to_ImageMetadata", to_ImageMetadata)
