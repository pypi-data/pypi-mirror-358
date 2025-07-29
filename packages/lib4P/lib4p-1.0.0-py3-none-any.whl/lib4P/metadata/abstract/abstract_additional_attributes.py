from ..interface.additional_attributes_interface import IAdditionalAttributes


class AbstractAdditionalAttributes(IAdditionalAttributes):
    """
    Abstract class defining various functions useful for managing additional attributes.
    """

    def __init__(self):
        super().__init__()
        self._additional_attributes = dict()

    def set_additional_attributes(self, attributes):
        """
        Set additional attributes related to the object.

        :param attributes: additional attributes to bind
        :type attributes: dict

        :note: existing additional attributes will be deleted.
        """
        if not isinstance(attributes, dict):
            raise TypeError(f"Argument 'attributes' must be of type {dict}, type {type(attributes)} found")
        self._additional_attributes.update(attributes)

    def get_additional_attributes(self):
        """
        Returns the additional attributes.
        Note that modifying a key in the returned dictionary will modify that value on the bound object.

        :return: additional attributes
        :rtype: dict
        """
        return self._additional_attributes

    def get_additional_attribute(self, attribute, default=None):
        """
        Returns the additional attribute corresponding to the key `attribute` or the value `default` if the key does not exist.

        :param attribute: requested `attribute` (key)
        :type attribute: str
        :param default: value to return if `attribute` does not exist
        :type default: Any
        :return: additional attribute corresponding to the key `attribute` or the value `default` if the key does not exist.
        """
        return self._additional_attributes.get(attribute, default)
