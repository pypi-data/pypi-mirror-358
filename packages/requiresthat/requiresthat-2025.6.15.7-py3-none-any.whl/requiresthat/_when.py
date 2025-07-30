"""When should a condition hold"""

from enum import Enum, auto

class When(Enum):
    APRIORI = auto()
    POSTMORTEM = auto()
    BEFOREANDAFTER = auto()
    # There is no DURING or INBETWEEN!

APRIORI = When.APRIORI
POSTMORTEM = When.POSTMORTEM
BEFOREANDAFTER = When.BEFOREANDAFTER
