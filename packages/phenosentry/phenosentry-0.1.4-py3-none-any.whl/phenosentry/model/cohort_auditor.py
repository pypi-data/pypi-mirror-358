import abc

from stairval import Auditor
from ..model import CohortInfo

class CohortAuditor(Auditor[CohortInfo], metaclass=abc.ABCMeta):
    """
        Abstract base class for auditing cohorts.

        This class extends the `Auditor` class with a generic type of `CohortInfo`
        and uses the `abc.ABCMeta` metaclass to enforce the implementation of abstract methods.

        Methods:
            id() -> str: Abstract method to return the unique identifier for the cohort auditor.
    """
    @abc.abstractmethod
    def id(self) -> str:
        return "default_cohort_auditor"
