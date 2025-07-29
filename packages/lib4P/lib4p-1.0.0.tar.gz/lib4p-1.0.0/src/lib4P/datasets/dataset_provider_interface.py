class DatasetProviderInterface(object):

    def has(self, dataset_name, **kwargs):
        """
        Returns True if a dataset named ``dataset_name`` exists.

        :param dataset_name: name of the dataset searched for
        :type dataset_name: str
        :param kwargs: additional arguments that may be required by the dataset provider
        :return: True if a dataset named ``dataset_name`` exists
        :rtype: bool
        """
        raise NotImplementedError

    def download(self, dataset_name, local_path, **kwargs):
        """
        Downloads the dataset ``dataset_name`` to the specified ``local_path`` folder.

        :param dataset_name: name of the dataset to download
        :type dataset_name: str
        :param local_path: download destination folder
        :type local_path: str
        :param kwargs: additional arguments that may be required by the dataset provider
        """
        raise NotImplementedError

    def list(self, **kwargs):
        """
        Lists all detected datasets.

        :param kwargs: additional arguments that may be required by the dataset provider
        :return: list of available dataset names
        :rtype: list[str]
        """
        raise NotImplementedError

    def detail(self, dataset_name, **kwargs):
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
        raise NotImplementedError
