from .additional_attributes_interface import IAdditionalAttributes
from .data_linker_interface import IDataLinker
from .metadata_linker_interface import IMetadataLinker


class ISensor(IMetadataLinker, IDataLinker, IAdditionalAttributes):

    def set_id(self, id):
        raise NotImplemented

    def get_id(self):
        raise NotImplemented

    def set_type(self, type):
        raise NotImplemented

    def get_type(self):
        raise NotImplemented

    def set_description(self, description):
        raise NotImplemented

    def get_description(self):
        raise NotImplemented

    def set_uri(self, uri):
        raise NotImplemented

    def get_uri(self):
        raise NotImplemented

    def set_serial_number(self, serial_number):
        raise NotImplemented

    def get_serial_number(self):
        raise NotImplemented

    def set_manufacturer(self, manufacturer):
        raise NotImplemented

    def get_manufacturer(self):
        raise NotImplemented

    def set_position(self, position):
        raise NotImplemented

    def get_position(self):
        raise NotImplemented
