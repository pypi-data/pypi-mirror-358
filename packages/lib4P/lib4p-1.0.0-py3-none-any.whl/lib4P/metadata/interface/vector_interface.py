from .additional_attributes_interface import IAdditionalAttributes
from .metadata_linker_interface import IMetadataLinker


class IVector(IMetadataLinker, IAdditionalAttributes):

    def set_id(self, id):
        raise NotImplemented

    def get_id(self):
        raise NotImplemented

    def set_uri(self, uri):
        raise NotImplemented

    def get_uri(self):
        raise NotImplemented

    def set_serial_number(self, serial_number):
        raise NotImplemented

    def get_serial_number(self):
        raise NotImplemented
