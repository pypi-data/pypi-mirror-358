from enum import Enum

class AuditorLevel(Enum):
    """
       Enum representing different levels of auditing.

       Attributes:
           DEFAULT (str): Represents the default auditing level.
           STRICT (str): Represents the strict auditing level.
    """
    DEFAULT = "default"
    STRICT = "strict"

    def __init__(self, level: int):
        self.level = level

    def __str__(self):
        return f"AuditorLevel(level={self.level})"

    def __repr__(self):
        return self.__str__()