from datetime import datetime

from .abstract.abstract_additional_attributes import AbstractAdditionalAttributes
from .abstract.abstract_metadata_linker import AbstractMetadataLinker
from .abstract.abstract_plot_linker import AbstractPlotLinker
from .abstract.abstract_sensor_linker import AbstractSensorLinker
from .interface.data_interface import IData


class Data(IData, AbstractMetadataLinker, AbstractSensorLinker, AbstractPlotLinker, AbstractAdditionalAttributes):

    def __init__(self, filename, name, date, **kwargs):
        """
        Data acquired by a given sensor during the measurement session.

        :param filename: path to the file containing the data
        :type filename: str
        :param name: common name assigned to this data (used for saving variants)
        :type name: str
        :param date: date (including time) of data acquisition
        :type date: str or datetime
        :param kwargs: additional attributes that can be linked to the object (example: 'plot_id' to which it is linked)

        :note: The scope of the `Data` class is metadata. Therefore, data (ex: RGB values, points cloud, etc.) are not
               directly contained in this class. It contains the elements necessary for its reading, namely a `filename`
               variable.
        """
        super().__init__()

        self._filename = None
        self.set_filename(filename)

        self._name = None
        self.set_name(name)

        self._date = None
        self.set_date(date)

        self.set_additional_attributes(kwargs)

    def __eq__(self, other):
        """
        Tests for equality between two `Data` objects.
        Equality is true when both objects are of type `Data`, and their `filename`, `name` and `date` values are equal to each other.

        :param other: another `Data` object
        :type other: Data
        :return: true if the two objects are equal
        :rtype: bool

        :note: The scope of the `Data` class is metadata. Therefore, only metadata is tested for equality, and in no case is the concrete data tested.
        """
        return (
            isinstance(other, IData)
            and self.get_filename() == other.get_filename()
            and self.get_name() == other.get_name()
            and self.get_date() == other.get_date()
            # and self.get_additional_attributes() == other.get_additional_attributes()
        )

    def set_filename(self, filename):
        """
        Set the path to the file containing the data.

        :param filename: path to the file containing the data
        :type filename: str

        :note: The `filename` member should include the `name` of the data as a subpart.
        """
        if not isinstance(filename, str):
            raise TypeError(f"Argument 'filename' must be of type {str}, "
                            f"type {type(filename)} found")
        self._filename = filename

    def get_filename(self):
        """
        Returns the path to the file containing the data.

        :return: path to the file containing the data
        :rtype: str
        """
        return self._filename

    def set_name(self, name):
        """
        Set the data name.

        :param name: data name
        :type name: str

        :note: The data name should be a subpart of `filename`.
        """
        if not isinstance(name, str):
            raise TypeError(f"Argument 'name' must be of type {str}, "
                            f"type {type(name)} found")
        self._name = name

    def get_name(self):
        """
        Returns the data name.

        :return: data name
        :rtype: str
        """
        return self._name

    def set_date(self, date):
        """
        Set the date the data was acquired.
        The date can be provided as a `datetime` or a string. In the case of a string, the pattern must match "%Y-%m-%d_%H:%M:%S" or "%Y-%m-%d_%H:%M:%S.%f".

        :param date: date the data was acquired
        :type date: datetime or str
        """
        if isinstance(date, str):
            date = datetime.strptime(date,
                                     "%Y-%m-%d_%H:%M:%S" + (".%f" if "." in date else ""))

        if not isinstance(date, datetime):
            raise TypeError(f"Argument 'date' must be of type {datetime}, "
                            f"type {type(date)} found")
        self._date = date

    def get_date(self):
        """
        Returns the date the data was acquired.

        :return: date the data was acquired
        :rtype: datetime
        """
        return self._date
