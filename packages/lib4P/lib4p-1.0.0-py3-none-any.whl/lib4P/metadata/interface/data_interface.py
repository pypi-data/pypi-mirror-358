from .additional_attributes_interface import IAdditionalAttributes
from .metadata_linker_interface import IMetadataLinker
from .plot_linker_interface import IPlotLinker
from .sensor_linker_interface import ISensorLinker


class IData(IMetadataLinker, ISensorLinker, IPlotLinker, IAdditionalAttributes):

    def set_filename(self, filename):
        raise NotImplemented

    def get_filename(self):
        raise NotImplemented

    def set_name(self, name):
        raise NotImplemented

    def get_name(self):
        raise NotImplemented

    def set_date(self, date):
        raise NotImplemented

    def get_date(self):
        raise NotImplemented
