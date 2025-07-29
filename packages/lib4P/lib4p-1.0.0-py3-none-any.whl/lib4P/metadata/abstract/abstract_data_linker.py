from ..interface.data_interface import IData
from ..interface.data_linker_interface import IDataLinker


class AbstractDataLinker(IDataLinker):
    """
    Abstract class defining various functions useful for linking one or more data instances to another object instance.
    """

    def __init__(self):
        super().__init__()
        self._data = list()

    def link_data(self, data):
        """
        Links a (list of) data to the current instance.

        Expands the list of linked data.

        :param data: (list of) data to link
        :type data: Data or list[Data]
        """
        if isinstance(data, (list, tuple)):
            for _data in data:
                self.link_data(_data)
        else:
            if not isinstance(data, IData):
                raise TypeError(f"Argument 'data' must be of type {IData}, "
                                f"type {type(data)} found")
            if data not in self._data:
                self._data.append(data)

    def has_data(self):
        """
        Returns True if a data is linked to the current instance.

        :return: True if a data is linked to the current instance
        :rtype: bool
        """
        return len(self._data) != 0

    def get_data(self):
        """
        Returns the list of data linked to the current instance (empty list if none linked).

        :return: list of data linked to the current instance (empty list if none linked)
        :rtype: List[Data]
        """
        return self._data
