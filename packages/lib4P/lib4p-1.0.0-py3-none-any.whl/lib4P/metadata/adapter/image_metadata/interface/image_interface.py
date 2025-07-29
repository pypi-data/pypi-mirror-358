from ....interface.data_interface import (IData)


class IImage(IData):

    def set_shutter_time(self, shutter_time):
        raise NotImplemented

    def get_shutter_time(self):
        raise NotImplemented

    def set_height(self, height):
        raise NotImplemented

    def get_height(self):
        raise NotImplemented

    def set_width(self, width):
        raise NotImplemented

    def get_width(self):
        raise NotImplemented

    def set_size(self, size):
        raise NotImplemented

    def get_size(self):
        raise NotImplemented

    @classmethod
    def from_data(cls, data):
        raise NotImplemented
