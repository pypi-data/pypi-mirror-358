from datetime import datetime

from .abstract.abstract_additional_attributes import AbstractAdditionalAttributes
from .abstract.abstract_metadata_linker import AbstractMetadataLinker
from .interface.session_interface import ISession


class Session(ISession, AbstractMetadataLinker, AbstractAdditionalAttributes):

    def __init__(self, date, experiment_id, experiment_uri, local_infrastructure, national_infrastructure, **kwargs):
        """
        Information about the measurement session

        :param date: date of the measurement session
        :type date: datetime or str
        :param experiment_id: experiment identifier
        :type experiment_id: str
        :param experiment_uri: URI associated with the experiment for the PHIS platform
        :type experiment_uri: str
        :param local_infrastructure: name of the local infrastructure (eg: name of the laboratory)
        :type local_infrastructure: str
        :param national_infrastructure: name of the national infrastructure (e.g. name of the consortium)
        :type national_infrastructure: str
        :param kwargs: additional attributes linked to the session (e.g. pilot, additional information, etc.)
        """
        super().__init__()
        self._date = None
        self.set_date(date)

        self._experiment_id = None
        self.set_experiment_id(experiment_id)

        self._experiment_uri = None
        self.set_experiment_uri(experiment_uri)

        self._local_infrastructure = None
        self.set_local_infrastructure(local_infrastructure)

        self._national_infrastructure = None
        self.set_national_infrastructure(national_infrastructure)

        self.set_additional_attributes(kwargs)

    def __eq__(self, other):
        """
        Tests for equality between two `Session` objects.
        Equality is true when both objects are of type `Session`, and their `date`, `experiment_id`, `experiment_uri`, `local_infrastructure` and `national_infrastructure` values are equal to each other.

        :param other: another `Session` object
        :type other: Session
        :return: true if the two objects are equal
        :rtype: bool
        """
        return (
                isinstance(other, ISession)
                and self.get_date() == other.get_date()
                and self.get_experiment_id() == other.get_experiment_id()
                and self.get_experiment_uri() == other.get_experiment_uri()
                and self.get_local_infrastructure() == other.get_local_infrastructure()
                and self.get_national_infrastructure() == other.get_national_infrastructure()
        )

    def set_date(self, date):
        """
        Set the date of the measurement session.
        The date can be provided as a `datetime` or a string. In the case of a string, the pattern must match "%Y-%m-%d_%H:%M:%S" or "%Y-%m-%d_%H:%M:%S.%f".

        :param date: date of the measurement session
        :type date: datetime or str
        """
        if isinstance(date, str):
            date = datetime.strptime(date,
                                     "%Y-%m-%d_%H:%M:%S" + (".%f" if "." in date else ""))

        if not isinstance(date, datetime):
            raise TypeError(f"Argument 'date' must be of type {datetime}, "
                            f"type {type(date)} found")
        self._date = date

    def get_date(self):
        """
        Returns the date of the measurement session.

        :return: date of the measurement session
        :rtype: datetime
        """
        return self._date

    def set_experiment_id(self, experiment_id):
        """
        Set the experiment identifier.

        :param experiment_id: experiment identifier
        :type experiment_id: str
        """
        if not isinstance(experiment_id, str):
            raise TypeError(f"Argument 'experiment_id' must be of type {str}, "
                            f"type {type(experiment_id)} found")
        self._experiment_id = experiment_id

    def get_experiment_id(self):
        """
        Returns the experiment identifier.

        :return: experiment identifier
        :rtype: str
        """
        return self._experiment_id

    def set_experiment_uri(self, experiment_uri):
        """
        Set the URI associated with the experiment for the PHIS platform.

        :param experiment_uri: URI associated with the experiment for the PHIS platform
        :type experiment_uri: str
        """
        if not isinstance(experiment_uri, str):
            raise TypeError(f"Argument 'experiment_uri' must be of type {str}, "
                            f"type {type(experiment_uri)} found")
        self._experiment_uri = experiment_uri

    def get_experiment_uri(self):
        """
        Returns the URI associated with the experiment for the PHIS platform.

        :return: URI associated with the experiment for the PHIS platform
        :rtype: str
        """
        return self._experiment_uri

    def set_local_infrastructure(self, local_infrastructure):
        """
        Set the name of the local infrastructure (eg: name of the laboratory).

        :param local_infrastructure: name of the local infrastructure (eg: name of the laboratory)
        :type local_infrastructure: str
        """

        if not isinstance(local_infrastructure, str):
            raise TypeError(f"Argument 'local_infrastructure' must be of type {str}, "
                            f"type {type(local_infrastructure)} found")
        self._local_infrastructure = local_infrastructure

    def get_local_infrastructure(self):
        """
        Returns the name of the local infrastructure (eg: name of the laboratory).

        :return: name of the local infrastructure (eg: name of the laboratory)
        :rtype: str
        """
        return self._local_infrastructure

    def set_national_infrastructure(self, national_infrastructure):
        """
        Set the name of the national infrastructure (e.g. name of the consortium).

        :param national_infrastructure: name of the national infrastructure (e.g. name of the consortium)
        :type national_infrastructure: str
        """
        if not isinstance(national_infrastructure, str):
            raise TypeError(f"Argument 'national_infrastructure' must be of type {str}, "
                            f"type {type(national_infrastructure)} found")
        self._national_infrastructure = national_infrastructure

    def get_national_infrastructure(self):
        """
        Returns the name of the national infrastructure (e.g. name of the consortium).

        :return: name of the national infrastructure (e.g. name of the consortium)
        :rtype: str
        """
        return self._national_infrastructure

