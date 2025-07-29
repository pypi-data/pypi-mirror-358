
class ParserInterface:

    version = None

    @staticmethod
    def from_dict(data, version=None):
        raise NotImplemented

    @staticmethod
    def to_dict(data, version=None):
        raise NotImplemented

