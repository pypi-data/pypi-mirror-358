from .. import parser_manager as ParserManager
from ..parser_interface import ParserInterface
from ... import Session
from ...interface.session_interface import ISession


class Parser(ParserInterface):

    version = (0, 0, 0)

    def __init__(self):
        self.sub_parsers = {
            "date": self.parse_date,
            "experiment_id": self.parse_experiment_id,
            "experiment_uri": self.parse_experiment_uri,
            "local_infra": self.parse_local_infrastructure,
            "national_infra": self.parse_national_infrastructure
        }

    def from_dict(self, data, version=None):
        version = ParserManager.parse_version(version) if version is not None else Parser.version
        kwargs = dict()
        for key in data:
            if key not in self.sub_parsers:
                attr, value = self.parse_additional_attribute(key, data[key], version=version)
            else:
                sub_parser = self.sub_parsers.get(key)
                attr, value = sub_parser(data[key], version=version)

            if attr is not None:
                kwargs[attr] = value

        return kwargs

    def to_dict(self, data, version=None):
        if not isinstance(data, ISession):
            raise TypeError(f"Argument 'data' must be of type {ISession}, type {type(data)} found")

        _additional_attributes = data.get_additional_attributes()

        return {
            **{key: value for key, value in _additional_attributes.items()},
            "date": data.get_date().strftime("%Y-%m-%d_%H:%M:%S"),
            "experiment_id": data.get_experiment_id(),
            "experiment_uri": data.get_experiment_uri(),
            "local_infra": data.get_local_infrastructure(),
            "national_infra": data.get_national_infrastructure()
        }

    def parse_date(self, date, version=None):
        return "date", date  # Date will be converted from str to datetime in Session instantiation

    def parse_experiment_id(self, experiment_id, version=None):
        return "experiment_id", experiment_id

    def parse_experiment_uri(self, experiment_uri, version=None):
        return "experiment_uri", experiment_uri

    def parse_local_infrastructure(self, local_infrastructure, version=None):
        return "local_infrastructure", local_infrastructure

    def parse_national_infrastructure(self, national_infrastructure, version=None):
        return "national_infrastructure", national_infrastructure

    def parse_additional_attribute(self, key, attribute, version=None):
        return key, attribute


ParserManager.register("session", Parser.version, Parser())
ParserManager.register(ISession, Parser.version, Parser())
ParserManager.register(Session, Parser.version, Parser())
