from .additional_attributes_interface import IAdditionalAttributes
from .data_linker_interface import IDataLinker
from .geolocation_linker_interface import IGeolocationLinker
from .metadata_linker_interface import IMetadataLinker


class IPlot(IMetadataLinker, IDataLinker, IGeolocationLinker, IAdditionalAttributes):

    def set_id(self, id):
        raise NotImplemented

    def get_id(self):
        raise NotImplemented

    def set_uri(self, uri):
        raise NotImplemented

    def get_uri(self):
        raise NotImplemented

    def set_coordinates(self, coordinates):
        raise NotImplemented

    def get_coordinates(self):
        raise NotImplemented

    def set_orientation(self, orientation):
        raise NotImplemented

    def get_orientation(self):
        raise NotImplemented
