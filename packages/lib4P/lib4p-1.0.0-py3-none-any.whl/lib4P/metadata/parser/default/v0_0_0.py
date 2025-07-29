from .. import parser_manager as ParserManager
from ..parser_interface import ParserInterface
from ...utils import is_equivalent_to_a_list


class Parser(ParserInterface):
    """
    The default parser parses not by key but by value (and its type)
    """

    version = (0, 0, 0)

    def from_dict(self, data, version=None):
        return data

    def to_dict(self, data, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        if (isinstance(data, int)
                or isinstance(data, str)
                or isinstance(data, bytes)
                or isinstance(data, bool)
                or isinstance(data, float)):
            return data

        if is_equivalent_to_a_list(data):
            return [self.to_dict(d) for d in data]

        if isinstance(data, ParserInterface):
            return data.to_dict(data, version=version)

        raise TypeError(f"Default parser cannot convert type {type(data)} into a dictionary."
                        f"Type {type(data)} does not implement the ParserInterface.")


ParserManager.register("default", Parser.version, Parser())
