import json
import os
import warnings

from .abstract.abstract_additional_attributes import AbstractAdditionalAttributes
from .interface.data_interface import IData
from .interface.geolocation_interface import IGeolocation
from .interface.metadata_interface import IMetadata
from .interface.plot_interface import IPlot
from .interface.sensor_interface import ISensor
from .interface.session_interface import ISession
from .interface.vector_interface import IVector
from .parser import parser_manager as ParserManager
from .utils import is_equivalent_to_a_list


class Metadata(IMetadata, AbstractAdditionalAttributes):

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
        super().__init__()
        self._session = None
        self.set_session(session)

        self._plots = None
        self.set_plots(plots)

        self._vector = None
        self.set_vector(vector)

        self._geolocations = None
        self.set_geolocations(geolocations)

        self._sensors = None
        self.set_sensors(sensors)

        self._data = None
        self.set_data(data)

        self._static_transforms = None
        self.set_static_transforms(static_transforms)

        self.set_additional_attributes(kwargs)

        self._version = None
        self._set_version_or_default(version)

        # Additional links
        self._link_data_and_sensors()
        self._link_data_and_plots()
        self._link_geolocations_and_plots()

    def __eq__(self, other):
        """
        Tests for equality between two `Metadata` objects.
        Equality is true when both objects are of type `Metadata`, and their `session`, `plots`, `vector`, `geolocations`, `sensors`, `data` and `static_transforms` values are equal to each other.
        See the `__eq__` functions for the corresponding object variables.

        :param other: another `Metadata` object
        :type other: IMetadata
        :return: true if the two objects are equal
        :rtype: bool
        """
        return (
            isinstance(other, IMetadata)
            and self.get_session() == other.get_session()
            and all([plot in other.get_plots() for plot in self.get_plots()])
            and all([plot in self.get_plots() for plot in other.get_plots()])
            and self.get_vector() == other.get_vector()
            and all([geolocation in other.get_geolocations() for geolocation in self.get_geolocations()])
            and all([geolocation in self.get_geolocations() for geolocation in other.get_geolocations()])
            and all([sensor in other.get_sensors() for sensor in self.get_sensors()])
            and all([sensor in self.get_sensors() for sensor in other.get_sensors()])
            and all([data in other.get_data() for data in self.get_data()])
            and all([data in self.get_data() for data in other.get_data()])
            # and self.get_static_transforms()  # TODO later
            # and self.get_additional_attributes()  # TODO later
            # and self._get_version() == other._get_version()  # Version is no longer test for equality (2 metadata file can be the same expect the version; so the format used, but having the same data inside)
        )

    def set_session(self, session):
        """
        Set the measurement session information.

        :param session: measurement session information
        :type session: ISession
        """
        if not isinstance(session, ISession):
            raise TypeError(f"Argument 'session' must be of type {ISession}, type {type(session)} found")
        session.link_metadata(self)
        self._session = session

    def get_session(self):
        """
        Returns the measurement session information.

        :return: measurement session information
        :rtype: ISession
        """
        return self._session

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
            plot.link_metadata(self)
        self._plots = plots

    def get_plots(self):
        """
        Returns the list of plots concerned by the measurement session.

        :return: list of plots concerned by the measurement session
        :rtype: list[IPlot]
        """
        return self._plots

    def get_plot(self):
        """
        Returns the plot concerned by the measurement session.
        If multiple plots are present, raises an error.

        :return: the plot concerned by the measurement session
        :rtype: IPlot

        :note: This function is only present for convenience in the case where a single plot is processed (saving the user from performing `get_plots()[0]` itself). The preferred way remains to loop over all the plots, without any a priori on their number.
        """
        if len(self._plots) != 1:
            raise IndexError(f"The 'get_plot' function can only be used when there is only one 'plot' in the list of "
                             f"plots, {len(self._plots)} elements found in the plots.")
        return self._plots[0]

    def set_vector(self, vector):
        """
        Set the vector used for the measurement session.

        :param vector: vector used for the measurement session
        :type vector: IVector
        """
        if not isinstance(vector, IVector):
            raise TypeError(f"Argument 'vector' must be of type {IVector}, type {type(vector)} found")
        vector.link_metadata(self)
        self._vector = vector

    def get_vector(self):
        """
        Returns the vector used for the measurement session.

        :return: vector used for the measurement session
        :rtype: IVector
        """
        return self._vector

    def set_geolocations(self, geolocations):
        """
        Set the list of geolocations concerned by the measurement session.

        :param geolocations: list of geolocations concerned by the measurement session
        :type geolocations: list[IGeolocation]
        """
        if not is_equivalent_to_a_list(geolocations):
            raise TypeError(f"Argument 'geolocations' must be of type {list} (or equivalent), "
                            f"type {type(geolocations)} found")
        if not all(isinstance(geolocation, IGeolocation) for geolocation in geolocations):
            raise TypeError(f"Elements of the 'geolocations' argument must be of type {IGeolocation}, "
                            f"at least one element is not of this type")
        for geolocation in geolocations:
            geolocation.link_metadata(self)
        self._geolocations = geolocations

    def get_geolocations(self):
        """
        Returns the list of geolocations concerned by the measurement session.

        :return: list of geolocations concerned by the measurement session
        :rtype: list[IGeolocation]
        """
        return self._geolocations

    def get_geolocation(self):
        """
        Returns the geolocation concerned by the measurement session.
        If multiple geolocations are present, raises an error.

        :return: the geolocation concerned by the measurement session
        :rtype: IGeolocation

        :note: This function is only present for convenience in the case where a single geolocation is processed (saving the user from performing `get_geolocations()[0]` itself). The preferred way remains to loop over all the geolocations, without any a priori on their number.
        """
        if len(self._geolocations) != 1:
            raise IndexError(f"The 'get_geolocation' function can only be used when there is only one 'geolocation' in the list of "
                             f"geolocations, {len(self._geolocations)} elements found in the geolocations.")
        return self._geolocations[0]

    def set_sensors(self, sensors):
        """
        Set the list of sensors used for the measurement session.

        :param sensors: list of sensors used for the measurement session
        :type sensors: list[ISensor]
        """
        if not is_equivalent_to_a_list(sensors):
            raise TypeError(f"Argument 'sensors' must be of type {list} (or equivalent), "
                            f"type {type(sensors)} found")
        if not all(isinstance(sensor, ISensor) for sensor in sensors):
            raise TypeError(f"Elements of the 'sensors' argument must be of type {ISensor}, "
                            f"at least one element is not of this type")
        for sensor in sensors:
            sensor.link_metadata(self)
        self._sensors = sensors

    def get_sensors(self):
        """
        Returns the list of sensors used for the measurement session.

        :return: list of sensors used for the measurement session
        :rtype: list[ISensor]
        """
        return self._sensors

    def set_data(self, data):
        """
        Set the list of data acquired by a given sensor during the measurement session.

        :param data: list of data acquired by a given sensor during the measurement session
        :type data: list[IData]
        """
        if not is_equivalent_to_a_list(data):
            raise TypeError(f"Argument 'data' must be of type {list} (or equivalent), "
                            f"type {type(data)} found")
        if not all(isinstance(_data, IData) for _data in data):
            raise TypeError(f"Elements of the 'data' argument must be of type {IData}, "
                            f"at least one element is not of this type")
        for _data in data:
            _data.link_metadata(self)
        self._data = data

    def get_data(self):
        """
        Returns the list of data acquired by a given sensor during the measurement session.

        :return: list of data acquired by a given sensor during the measurement session
        :rtype: list[IData]
        """
        return self._data

    def get_data_from_filename(self, filename):
        """
        Returns the Data (metadata) corresponding to the specified `filename`.
        Returns None if no match is found.

        :param filename: filename searched
        :type filename: str
        :return: IData or None
        """
        for _data in self.get_data():
            if _data.get_filename() == filename:
                return _data
        return None

    def set_static_transforms(self, static_transforms):
        """
        [TODO] Not enough information about this argument

        :param static_transforms:
        """
        self._static_transforms = static_transforms
        # TODO : Gérer ce setter plus pérennement (aucun check actuellement, etc.) => D'abord besoin de comprendre
        #        les tenant et aboutissant de ces données

    def get_static_transforms(self):
        """
        [TODO] Not enough information about this argument

        :return:
        """
        return self._static_transforms

    def _set_version_or_default(self, version=None):
        """
        Set the specified version or set a default version corresponding to the highest version of the parsers.

        :param version: metadata format version
        :type version: str or tuple
        """
        if version is None:
            version = ParserManager.get_latest_version()
            if version is None:
                raise Exception("Cannot retrieve a default version automatically")
            self._set_version_or_default(version)
        else:
            if isinstance(version, str):
                version = ParserManager.parse_version(version)
            ParserManager.check_version(version)
            self._version = version

    def _get_version(self):
        """
        Returns the metadata format version.

        :return: metadata format version
        :rtype: tuple
        """
        return self._version

    def _link_data_and_sensors(self):
        """
        Private methods for defining connections between Data and Sensor.

        Once executed, on a given data `my_data`, the method `my_data.get_sensor()` will return the sensor (instance) that acquired this data.
        Conversely, a `my_sensor` sensor will return the list of data acquired with the `my_sensor.get_data()` method.
        """
        for _data in self.get_data():
            # Get Sensor ID by additional attributes or by current Sensor linked
            sensor_id = _data.get_additional_attribute("sensor_id", None)
            if sensor_id is None and _data.has_sensor():
                sensor_id = _data.get_sensor().get_id()

            if sensor_id is None:
                continue  # Skip the binding if no sensor_id detected

            sensors = [sensor for sensor in self.get_sensors() if sensor.get_id() == sensor_id]

            if len(sensors) == 1:  # Otherwise do nothing
                sensor = sensors[0]
                sensor.link_data(_data)
                _data.link_sensor(sensor)

    def _link_data_and_plots(self):
        """
        Private methods for defining connections between Data and Plot.

        Once executed, on a given data `my_data`, the method `my_data.get_plot()` will return the plot (instance) concerned by this data.
        Conversely, a `my_plot` plot will return the list of data concerning it with the `my_plot.get_data()` method.
        """
        for _data in self.get_data():
            plot_id = _data.get_additional_attribute("plot_id")
            if plot_id is not None:
                for plot in self.get_plots():
                    if plot.get_id() == plot_id:
                        _data.link_plot(plot)
                        plot.link_data(_data)
                        continue

    def _link_geolocations_and_plots(self):
        """
        Private methods for defining connections between Geolocation and Parcel.

        Once executed, on a given geolocation `my_geolocation`, the method `my_geolocation.get_plot()` will return the plot (instance) concerned by this geolocation.
        Conversely, a `my_plot` plot will return the geolocation concerned with the `my_plot.get_geolocation()` method.
        """
        for geolocation in self.get_geolocations():
            plot_id = geolocation.get_additional_attribute("plot_id")
            if plot_id is not None:
                for plot in self.get_plots():
                    if plot.get_id() == plot_id:
                        geolocation.link_plot(plot)
                        plot.link_geolocation(geolocation)
                        continue

    def extend(self, metadata):
        """
        Extends the current Metadata by merging the second Metadata object provided.

        The only thing that will be checked is that the second object is of type Metadata and that their Session and Vector values match.

        :param metadata: another Metadata object
        :type metadata: IMetadata

        :warning: Merging is done in-place, so any errors raised may result in corruption of the original metadata. It is therefore not recommended to use this method in a try-catch statement.
        """
        if not isinstance(metadata, IMetadata):
            raise TypeError(f"Argument 'metadata' must be of type {IMetadata}, "
                            f"type {type(metadata)} found")

        if self.get_session() != metadata.get_session():
            raise ValueError("Only metadata from the same session can be merged")

        if self.get_vector() != metadata.get_vector():
            raise ValueError("Metadata from the same session should have the same vector values")

        geolocations = self.get_geolocations()
        for geolocation in metadata.get_geolocations():
            if geolocation not in geolocations:
                geolocations.append(geolocation)
        self.set_geolocations(geolocations)

        plots = self.get_plots()
        for plot in metadata.get_plots():
            if plot not in plots:
                plots.append(plot)
        self.set_plots(plots)

        sensors = self.get_sensors()
        for sensor in metadata.get_sensors():
            if sensor not in sensors:
                sensors.append(sensor)
        self.set_sensors(sensors)

        data = self.get_data()
        for _data in metadata.get_data():
            if _data not in data:
                data.append(_data)
        self.set_data(data)

        static_transforms = self.get_static_transforms()
        for static_transform in metadata.get_static_transforms():
            if static_transform not in static_transforms:
                static_transforms.append(static_transform)
        self.set_static_transforms(static_transforms)

        self._link_data_and_sensors()  # Note : actuellement, le linkage des données n'est pas nettoyé, donc il peut
        #                                       théoriquement rester des traces de données précédemment liées. Dans la
        #                                       pratique, ça n'est normalement pas un cas possible.
        self._link_data_and_plots()
        self._link_geolocations_and_plots()

    @staticmethod
    def _warn_about_version(version):
        version = ParserManager.parse_version(version)
        version_str = ".".join([str(v) for v in version])
        if version > ParserManager.get_latest_version():
            latest_version_str = ".".join([str(v) for v in ParserManager.get_latest_version()])
            warnings.warn(f"The detected metadata version ({version_str}) is higher than "
                          f"the defined parsers ({latest_version_str}). "
                          "This may indicate a need to update the 4P library.",
                          category=FutureWarning, skip_file_prefixes=(os.path.dirname(__file__),))
        elif not ParserManager.does_version_exists(version):
            warnings.warn(f"The detected metadata version ({version_str}) does not appear to match any parser version. "
                          "This can cause unexpected behavior. "
                          "It may also indicate a need to update the 4P library.",
                          category=RuntimeWarning, skip_file_prefixes=(os.path.dirname(__file__),))

    @classmethod
    def from_dict(cls, data):
        """
        Creates a Metadata instance from a dictionary.
        This dictionary must correspond to reading a metadata JSON file.

        :param data: dictionary containing metadata
        :type data: dict
        :return: Metadata instance
        :rtype: Metadata
        """
        if not isinstance(data, dict):
            raise TypeError(f"Argument 'data' must be of type {dict} to be parsed")

        # Detect metadata version format
        metadata_format_version = data["metadata_version"] if "metadata_version" in data else "0.0.0"

        # Parse
        cls._warn_about_version(metadata_format_version)
        parser = ParserManager.get_parser("metadata", metadata_format_version)

        kwargs = parser.from_dict(data, metadata_format_version)
        if "version" not in kwargs:
            kwargs["version"] = parser.version
        metadata = cls(**kwargs)

        return metadata

    def to_dict(self, version=None):
        """
        Transforms a Metadata instance into a dictionary.

        The `version` argument allows you to specify the format to follow for the resulting dictionary.
        If not specified, the fixed version is the one specified in the Metadata instance.

        :param version: metadata format version
        :type version: str or tuple
        :return: metadata in dictionary form
        :rtype: dict
        """
        if version is None:
            version = self._get_version()

        self._warn_about_version(version)
        parser = ParserManager.get_parser("metadata", version)
        dic = parser.to_dict(self, version)

        return dic

    @classmethod
    def load(cls, filepath):
        """
        Creates a Metadata instance from reading a file.

        The file to read must be in JSON format and present the different keys necessary for building a Metadata instance.

        :param filepath: path to file to read
        :type filepath: str
        :return: Metadata instance
        :rtype: Metadata
        """
        with open(filepath, "r") as file:
            data = json.load(file)
            return cls.from_dict(data)

    def to_json(self, filepath, version=None, **kwargs):
        """
        Converts and writes a Metadata instance to JSON format.

        The `version` argument allows you to specify the format to follow for the resulting data.
        If not specified, the fixed version is the one specified in the Metadata instance.

        :param filepath: path to file to write
        :type filepath: str
        :param version: metadata format version
        :type version: str or tuple
        :param kwargs: additional arguments to pass to the JSON serialization function `json.dump` (ex: `indent=None` to compact the output)
        """
        with open(filepath, "w") as file:
            data = self.to_dict(version)
            _kwargs = dict(indent=4)
            _kwargs.update(kwargs)
            json.dump(data, file, **_kwargs)

    @classmethod
    def read(cls, filepath):
        """
        Alias of the `load` method.
        """
        return cls.load(filepath)

    def write(self, filepath, version=None, **kwargs):
        """
        Alias of the `to_json` method.
        """
        return self.to_json(filepath, version, **kwargs)

    def save(self, filepath, version=None, **kwargs):
        """
        Alias of the `to_json` method.
        """
        return self.to_json(filepath, version, **kwargs)
