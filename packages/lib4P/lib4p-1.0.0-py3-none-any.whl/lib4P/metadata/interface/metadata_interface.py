from .additional_attributes_interface import IAdditionalAttributes


class IMetadata(IAdditionalAttributes):

    def set_session(self, session):
        raise NotImplemented

    def get_session(self):
        raise NotImplemented

    def set_plots(self, plots):
        raise NotImplemented

    def get_plots(self):
        raise NotImplemented

    def get_plot(self):
        raise NotImplemented

    def set_vector(self, vector):
        raise NotImplemented

    def get_vector(self):
        raise NotImplemented

    def set_geolocations(self, geolocation):
        raise NotImplemented

    def get_geolocations(self):
        raise NotImplemented

    def get_geolocation(self):
        raise NotImplemented

    def set_sensors(self, sensors):
        raise NotImplemented

    def get_sensors(self):
        raise NotImplemented

    def set_data(self, images):
        raise NotImplemented

    def get_data(self):
        raise NotImplemented

    def set_static_transforms(self, static_transforms):
        raise NotImplemented

    def get_static_transforms(self):
        raise NotImplemented

    def _set_version_or_default(self, version=None):
        raise NotImplemented

    def _get_version(self):
        raise NotImplemented

    def extend(self, metadata):
        raise NotImplemented

    @staticmethod
    def from_dict(data):
        raise NotImplemented

    def to_dict(self, version=None):
        raise NotImplemented

    @staticmethod
    def load(filepath):
        raise NotImplemented
