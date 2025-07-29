from enum import Enum


class AbstractionLevel(Enum):
    """
    Enum class for default abstraction levels.
    """

    RESIMULATION = 0
    DELAY = 1
    DEMAND = 2
    INFRASTRUCTURE = 3
    RANDOM = 4
