import abc

from stairval import Auditor
from ..model import PhenopacketInfo


class PhenopacketAuditor(Auditor[PhenopacketInfo], metaclass=abc.ABCMeta):
    """
    Represents information about a cohort of phenopackets.

    Attributes:
        name (str): The name of the cohort.
        path (str): The file path to the cohort directory or file.
        phenopackets (typing.Collection[PhenopacketInfo]): A collection of PhenopacketInfo objects representing the phenopackets in the cohort.
    """
    @abc.abstractmethod
    def id(self) -> str:
        return "default_phenopacket_auditor"