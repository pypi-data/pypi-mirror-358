from ..interface.geolocation_interface import IGeolocation
from ..interface.geolocation_linker_interface import IGeolocationLinker


class AbstractGeolocationLinker(IGeolocationLinker):
    """
    Abstract class defining various functions useful for binding a geolocation instance to another object instance.
    """

    def __init__(self):
        super().__init__()
        self._geolocation = None

    def link_geolocation(self, geolocation):
        """
        Links a geolocation to the current instance.

        Only one geolocation can be linked.

        :param geolocation: geolocation to link
        :type geolocation: Geolocation
        """
        if not isinstance(geolocation, IGeolocation):
            raise TypeError(f"Argument 'geolocation' must be of type {IGeolocation}, "
                            f"type {type(geolocation)} found")
        self._geolocation = geolocation

    def has_geolocation(self):
        """
        Returns True if a geolocation is linked to the current instance.

        :return: True if a geolocation is linked to the current instance
        :rtype: bool
        """
        return self._geolocation is not None

    def get_geolocation(self):
        """
        Returns the geolocation linked to the current instance (None if not linked).

        :return: geolocation linked to the current instance (None if not linked)
        :rtype: Geolocation or None
        """
        return self._geolocation
