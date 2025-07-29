import os

import owncloud

from .dataset_provider_interface import DatasetProviderInterface


# https://github.com/owncloud/pyocclient
class NextCloudDatasetProvider(DatasetProviderInterface):
    def __init__(self, public_link):
        """
        NextCloud repository-based dataset provider.

        :param public_link: Public URL corresponding to the folder containing the datasets-folders.
        :type public_link: str
        """
        self.oc = owncloud.Client.from_public_link(public_link)

    def has(self, dataset_name, **kwargs):
        return dataset_name in self.list()

    def download(self, dataset_name, local_path, **kwargs):
        if not self.has(dataset_name):
            raise Exception(f'No dataset named "{dataset_name}" found')
        self._download_directory(dataset_name, local_path)

    def _download_directory(self, remote_directory_path, local_path):
        os.makedirs(local_path, exist_ok=True)
        for file in self.oc.list(remote_directory_path):
            if file.file_type == "file":
                self.oc.get_file(file.path, os.path.join(local_path, file.name))
            elif file.file_type == "dir":
                self._download_directory(file.path,  # os.path.join(remote_directory_path, file.name),
                                         os.path.join(local_path, file.name))
            else:
                raise TypeError(f"Unknown type {file.file_type}, not able to download")

    def list(self, **kwargs):
        return [file.name for file in self.oc.list(".") if file.file_type == "dir"]

    def detail(self, dataset_name, **kwargs):
        if not self.has(dataset_name):
            raise Exception(f'No dataset named "{dataset_name}" found')
        if any([file.name == "dataset_metadata.json" for file in self.oc.list(dataset_name)]):
            return self.oc.get_file_contents(os.path.join(dataset_name, "dataset_metadata.json")).decode("utf-8")
        else:
            return "No details or missing 'dataset_metadata.json' file for the specified dataset"

