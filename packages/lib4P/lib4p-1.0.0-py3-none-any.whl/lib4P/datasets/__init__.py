import os

from .dataset_provider_interface import DatasetProviderInterface
from .nextcloud_dataset_provider import NextCloudDatasetProvider


class Datasets:
    """
    Class providing a simple interface for listing, detailing, and downloading datasets.
    """
    _dataset_provider = NextCloudDatasetProvider("https://nextcloud.inrae.fr/s/GxQiqC67i9sdiGK")

    @staticmethod
    def has(dataset_name, **kwargs):
        """
        Returns True if a dataset named ``dataset_name`` exists.

        :param dataset_name: name of the dataset searched for
        :type dataset_name: str
        :param kwargs: additional arguments that may be required by the dataset provider
        :return: True if a dataset named ``dataset_name`` exists
        :rtype: bool
        """
        return Datasets._dataset_provider.has(dataset_name, **kwargs)

    @staticmethod
    def download(dataset_name, local_path=None, **kwargs):
        """
        Downloads the dataset ``dataset_name`` to the specified ``local_path`` folder.
        If ``local_path`` is not specified, the destination folder will be a folder with the same name as the dataset in
        the current working directory.

        :param dataset_name: name of the dataset to download
        :type dataset_name: str
        :param local_path: download destination folder
        :type local_path: str | None
        :param kwargs: additional arguments that may be required by the dataset provider

        :note: This method only uses the specialized method of the dataset provider. All functionality (progress bar,
               cache, etc.) is therefore the responsibility of this provider.
        """
        if local_path is None:
            local_path = os.path.join("./", dataset_name)
        return Datasets._dataset_provider.download(dataset_name, local_path, **kwargs)

    @staticmethod
    def list(**kwargs):
        """
        Lists all detected datasets.

        :param kwargs: additional arguments that may be required by the dataset provider
        :return: list of available dataset names
        :rtype: list[str]
        """
        return Datasets._dataset_provider.list(**kwargs)

    @staticmethod
    def detail(dataset_name, **kwargs):
        """
        Provides information about the dataset ``dataset_name``.

        :param dataset_name: name of the dataset to detail
        :type dataset_name: str
        :param kwargs: additional arguments that may be required by the dataset provider
        :return: information about the dataset
        :rtype: str | Any | None

        :note: The generic return type is ``str`` but can differ depending on the dataset provider,
               including JSON, XML, plain text, or an object structure.
        """
        return Datasets._dataset_provider.detail(dataset_name, **kwargs)

    @staticmethod
    def set_dataset_provider(dataset_provider):
        """
        Replaces the default dataset provider with the new ``dataset_provider``.

        :param dataset_provider: new dataset provider to set (must implement :py:class:`DatasetProviderInterface`)
        :type dataset_provider: DatasetProviderInterface
        """
        if not isinstance(dataset_provider, DatasetProviderInterface):
            raise TypeError(f'The argument "dataset_provider" must be of type DatasetProviderInterface, \
                            {type(dataset_provider)} found')
        Datasets._dataset_provider = dataset_provider
