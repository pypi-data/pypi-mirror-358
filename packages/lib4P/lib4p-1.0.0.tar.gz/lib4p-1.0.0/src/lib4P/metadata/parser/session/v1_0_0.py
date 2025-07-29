from .v0_0_0 import Parser as PreviousParser
from .. import parser_manager as ParserManager
from ... import Session
from ...interface.session_interface import ISession


class Parser(PreviousParser):  # ParserInterface already inherits from PreviousParser

    version = (1, 0, 0)

    def __init__(self):
        PreviousParser.__init__(self)

        del self.sub_parsers["local_infra"]
        del self.sub_parsers["national_infra"]

        self.sub_parsers.update({
            "local_infrastructure": self.parse_local_infrastructure,
            "national_infrastructure": self.parse_national_infrastructure
        })

    def to_dict(self, data, version=None):
        if not isinstance(data, ISession):
            raise TypeError(f"Argument 'data' must be of type {ISession}, type {type(data)} found")

        _additional_attributes = data.get_additional_attributes()

        return {
            **{key: value for key, value in _additional_attributes.items()},
            "date": data.get_date().strftime("%Y-%m-%d_%H:%M:%S"),
            "experiment_id": data.get_experiment_id(),
            "experiment_uri": data.get_experiment_uri(),
            "local_infrastructure": data.get_local_infrastructure(),
            "national_infrastructure": data.get_national_infrastructure()
        }


ParserManager.register("session", Parser.version, Parser())
ParserManager.register(ISession, Parser.version, Parser())
ParserManager.register(Session, Parser.version, Parser())
