from ..interface.metadata_interface import IMetadata
from ..interface.metadata_linker_interface import IMetadataLinker


class AbstractMetadataLinker(IMetadataLinker):
    """
    Abstract class defining various functions useful for binding a metadata instance to another object instance.
    """

    def __init__(self):
        super().__init__()
        self._metadata = None

    def link_metadata(self, metadata):
        """
        Links a metadata to the current instance.

        Only one metadata can be linked.

        :param metadata: metadata to link
        :type metadata: Metadata
        """
        if not isinstance(metadata, IMetadata):
            raise TypeError(f"Argument 'metadata' must be of type {IMetadata}, "
                            f"type {type(metadata)} found")
        self._metadata = metadata

    def has_metadata(self):
        """
        Returns True if a metadata is linked to the current instance.

        :return: True if a metadata is linked to the current instance
        :rtype: bool
        """
        return self._metadata is not None

    def get_metadata(self):
        """
        Returns the metadata linked to the current instance (None if not linked).

        :return: metadata linked to the current instance (None if not linked)
        :rtype: Metadata or None
        """
        return self._metadata
