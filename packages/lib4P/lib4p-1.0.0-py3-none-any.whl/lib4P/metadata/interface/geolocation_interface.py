from .additional_attributes_interface import IAdditionalAttributes
from .metadata_linker_interface import IMetadataLinker
from .plot_linker_interface import IPlotLinker


class IGeolocation(IMetadataLinker, IPlotLinker, IAdditionalAttributes):

    def set_filename(self, filename):
        raise NotImplemented

    def get_filename(self):
        raise NotImplemented
