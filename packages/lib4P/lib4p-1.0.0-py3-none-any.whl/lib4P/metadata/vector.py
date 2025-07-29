from .abstract.abstract_additional_attributes import AbstractAdditionalAttributes
from .abstract.abstract_metadata_linker import AbstractMetadataLinker
from .interface.vector_interface import IVector


class Vector(IVector, AbstractMetadataLinker, AbstractAdditionalAttributes):

    def __init__(self, id, uri, serial_number, **kwargs):
        """
        Vector used for the measurement session.

        :param id: vector identifier
        :type id: str
        :param uri: URI associated with the vector for the PHIS platform
        :type uri: str
        :param serial_number: vector serial number
        :type serial_number: str
        :param kwargs: additional attributes linked to the vector (e.g. acquisition version, format version, etc.)
        """
        super().__init__()
        self._id = None
        self.set_id(id)

        self._uri = None
        self.set_uri(uri)

        self._serial_number = None
        self.set_serial_number(serial_number)

        self.set_additional_attributes(kwargs)

    def __eq__(self, other):
        """
        Tests for equality between two `Vector` objects.
        Equality is true when both objects are of type `Vector`, and their `id`, `uri` and `serial_number` values are equal to each other.

        :param other:
        :return:
        """
        return (
            isinstance(other, IVector)
            and self.get_id() == other.get_id()
            and self.get_uri() == other.get_uri()
            and self.get_serial_number() == other.get_serial_number()
        )

    def set_id(self, id):
        """
        Set the vector identifier.

        :param id: vector identifier
        :type id: str
        """
        if not isinstance(id, str):
            raise TypeError(f"Argument 'id' must be of type {str}, type {type(id)} found")
        if id == "":
            raise ValueError("Argument 'id' must not be empty")
        self._id = id

    def get_id(self):
        """
        Returns the vector identifier.

        :return: vector identifier
        :rtype: str
        """
        return self._id

    def set_uri(self, uri):
        """
        Set the URI associated with the vector for the PHIS platform.

        :param uri: URI associated with the vector for the PHIS platform
        :type uri: str
        """
        if not isinstance(uri, str):
            raise TypeError(f"Argument 'uri' must be of type {str}, type {type(uri)} found")
        self._uri = uri

    def get_uri(self):
        """
        Returns the URI associated with the vector for the PHIS platform

        :return: URI associated with the sensor for the PHIS platform
        :rtype: str
        """
        return self._uri

    def set_serial_number(self, serial_number):
        """
        Set the vector serial number.

        :param serial_number: vector serial number
        :type serial_number: str
        """
        if not isinstance(serial_number, str):
            raise TypeError(f"Argument 'serial_number' must be of type {str}, type {type(serial_number)} found")
        self._serial_number = serial_number

    def get_serial_number(self):
        """
        Returns the vector serial number.

        :return: vector serial number
        :rtype: str
        """
        return self._serial_number

    def is_phenomobile(self):
        raise NotImplemented
        # TODO : Throw a warning about the limited reliability of this function         => Via un decorator ? -> Pourrait permettre de ne le lancer qu'une seule fois au premier appel ==> Bibliothèque warnings permet ça

    def is_literal(self):
        raise NotImplemented
        # TODO : Throw a warning about the limited reliability of this function         => Via un decorator ? -> Pourrait permettre de ne le lancer qu'une seule fois au premier appel ==> Bibliothèque warnings permet ça

    def is_uav(self):
        raise NotImplemented
        # TODO : Throw a warning about the limited reliability of this function         => Via un decorator ? -> Pourrait permettre de ne le lancer qu'une seule fois au premier appel ==> Bibliothèque warnings permet ça
