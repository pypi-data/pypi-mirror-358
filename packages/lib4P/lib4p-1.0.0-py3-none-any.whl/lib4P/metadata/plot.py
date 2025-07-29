import numbers

from .abstract.abstract_additional_attributes import AbstractAdditionalAttributes
from .abstract.abstract_geolocation_linker import AbstractGeolocationLinker
from .abstract.abstract_data_linker import AbstractDataLinker
from .abstract.abstract_metadata_linker import AbstractMetadataLinker
from .interface.plot_interface import IPlot
from .utils import is_equivalent_to_a_list


class Plot(IPlot, AbstractMetadataLinker, AbstractDataLinker, AbstractGeolocationLinker, AbstractAdditionalAttributes):

    def __init__(self, id, uri, coordinates, orientation, **kwargs):
        """
        Plot concerned by the measurement session.

        :param id: plot identifier
        :type id: str
        :param uri: URI associated with the plot for the PHIS platform
        :type uri: str
        :param coordinates: coordinates (longitude and latitude) forming the polygon of the plot
        :type coordinates: list of pair (longitude, latitude)
        :param orientation: [hazardous] plot orientation
        :type orientation: float
        :param kwargs: additional attributes linked to the plot (e.g. variety, row spacing, etc.)
        """
        super().__init__()
        self._id = None
        self.set_id(id)

        self._uri = None
        self.set_uri(uri)

        self._coordinates = None
        self.set_coordinates(coordinates)

        self._orientation = None
        self.set_orientation(orientation)

        self.set_additional_attributes(kwargs)

    def __eq__(self, other):
        """
        Tests for equality between two `Plot` objects.
        Equality is true when both objects are of type `Plot`, and their `id`, `uri`, `coordinates` and `orientation` values are equal to each other.

        :param other: another `Plot` object
        :type other: Plot
        :return: true if the two objects are equal
        :rtype: bool
        """
        return (
            isinstance(other, IPlot)
            and self.get_id() == other.get_id()
            and self.get_uri() == other.get_uri()
            and self.get_coordinates() == other.get_coordinates()
            and self.get_orientation() == other.get_orientation()
        )

    def set_id(self, id):
        """
        Set the plot identifier.

        :param id: plot identifier
        :type id: str
        """
        if not isinstance(id, str):
            raise TypeError(f"Argument 'id' must be of type {str}, type {type(id)} found")
        self._id = id

    def get_id(self):
        """
        Returns the plot identifier.

        :return: plot identifier
        :rtype: str
        """
        return self._id

    def set_uri(self, uri):
        """
        Set the URI associated with the plot for the PHIS platform.

        :param uri: URI associated with the plot for the PHIS platform
        :type uri: str
        """
        if not isinstance(uri, str):
            raise TypeError(f"Argument 'uri' must be of type {str}, type {type(uri)} found")
        self._uri = uri

    def get_uri(self):
        """
        Returns the URI associated with the plot for the PHIS platform.

        :return: URI associated with the plot for the PHIS platform
        :rtype: str
        """
        return self._uri

    def set_coordinates(self, coordinates):
        """
        Set the coordinates (longitude and latitude) forming the polygon of the plot.

        :param coordinates: coordinates (longitude and latitude) forming the polygon of the plot
        :type coordinates: list of pair (longitude, latitude)
        """
        if not is_equivalent_to_a_list(coordinates):
            raise TypeError(f"Argument 'coordinates' must be of type {list} (or equivalent), "
                            f"type {type(coordinates)} found")
        _coordinates = []
        for coordinate in coordinates:
            if not is_equivalent_to_a_list(coordinate):
                raise TypeError(f"Elements of the 'coordinates' argument must be of type {list} (or equivalent), "
                                f"type {type(coordinate)} found")
            if len(coordinate) != 2:
                raise ValueError(f"Elements of the 'coordinates' argument must only correspond to pairs of value, "
                                 f"{len(coordinate)} values found")
            if not all([isinstance(value, numbers.Number) and not isinstance(value, bool) for value in coordinate]):
                raise TypeError(f"The values of the elements of the 'coordinates' argument must be numeric values")

            _coordinates.append(list(coordinate))

        # Suppress closing if equal to opening
        if len(_coordinates) > 1 and _coordinates[0] == _coordinates[-1]:
            del _coordinates[-1]

        self._coordinates = _coordinates

    def get_coordinates(self, closed=False):
        """
        Returns the coordinates (longitude and latitude) forming the polygon of the plot.

        :param closed: indicates whether the returned coordinates are closing, i.e. the last and first coordinates are equal
        :type closed: bool
        :return: coordinates (longitude and latitude) forming the polygon of the plot
        :rtype: list of pair (longitude, latitude)
        """
        return self._coordinates+[self._coordinates[0]] if closed else self._coordinates

    def set_orientation(self, orientation):
        """
        Set the plot orientation.

        :param orientation: plot orientation
        :type orientation: float

        :warning: not enough details on the specified value
        """
        if not isinstance(orientation, numbers.Number) or isinstance(orientation, bool):
            raise TypeError(f"Argument 'orientation' must be numeric value, type {type(orientation)} found")

        self._orientation = orientation

    def get_orientation(self):
        """
        Returns the plot orientation.

        :return: plot orientation
        :rtype: float

        :warning: not enough details on the specified value
        """
        return self._orientation
