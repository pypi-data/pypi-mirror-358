from .abstract.abstract_additional_attributes import AbstractAdditionalAttributes
from .abstract.abstract_metadata_linker import AbstractMetadataLinker
from .abstract.abstract_plot_linker import AbstractPlotLinker
from .interface.geolocation_interface import IGeolocation


class Geolocation(IGeolocation, AbstractMetadataLinker, AbstractPlotLinker, AbstractAdditionalAttributes):

    def __init__(self, filename, **kwargs):
        """
        Geolocation of the vector during the measurement session.

        :param filename: path to the file containing the geolocation data
        :type filename: str
        :param kwargs: additional attributes that can be linked to the object (example: 'plot_id' to which it is linked)

        :note: The scope of the `Geolocation` class is metadata. Therefore, the geolocation data is not directly
               contained in this class. It contains the elements necessary for its reading, namely a `filename` variable.
        """
        super().__init__()
        self._filename = None
        self.set_filename(filename)

        self.set_additional_attributes(kwargs)

    def __eq__(self, other):
        """
        Tests for equality between two `Geolocation` objects.
        Equality is true when both objects are of type `Geolocation`, and their `filename` values are equal.

        :param other: another `Geolocation` object
        :type other: Geolocation
        :return: true if the two objects are equal
        :rtype: bool

        :note: The scope of the `Geolocation` class is metadata. Therefore, only metadata is tested for equality, and in no case is the concrete data tested.
        """
        return (
            isinstance(other, IGeolocation)
            and self.get_filename() == other.get_filename()
        )

    def set_filename(self, filename):
        """
        Set the path to the file containing the geolocation data.

        :param filename: path to the file containing the geolocation data
        :type filename: str
        """
        if not isinstance(filename, str):
            raise TypeError(f"Argument 'filename' must be of type {str}, type {type(filename)} found")
        self._filename = filename

    def get_filename(self):
        """
        Returns the path to the file containing the geolocation data.

        :return: path to the file containing the geolocation data
        :rtype: str
        """
        return self._filename
