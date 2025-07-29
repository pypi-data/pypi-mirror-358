from .additional_attributes_interface import IAdditionalAttributes
from .metadata_linker_interface import IMetadataLinker


class ISession(IMetadataLinker, IAdditionalAttributes):

    def set_date(self, date):
        raise NotImplemented

    def get_date(self):
        raise NotImplemented

    def set_experiment_id(self, experiment_id):
        raise NotImplemented

    def get_experiment_id(self):
        raise NotImplemented

    def set_experiment_uri(self, experiment_uri):
        raise NotImplemented

    def get_experiment_uri(self):
        raise NotImplemented

    def set_local_infrastructure(self, local_infrastructure):
        raise NotImplemented

    def get_local_infrastructure(self):
        raise NotImplemented

    def set_national_infrastructure(self, national_infrastructure):
        raise NotImplemented

    def get_national_infrastructure(self):
        raise NotImplemented
