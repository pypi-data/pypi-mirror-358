"""When should a condition hold"""

from enum import Flag, auto

class When(Flag):
    APRIORI = auto()
    POSTMORTEM = auto()
    BEFOREANDAFTER = APRIORI | POSTMORTEM
    # There is no DURING or INBETWEEN!

APRIORI = When.APRIORI
POSTMORTEM = When.POSTMORTEM
BEFOREANDAFTER = When.BEFOREANDAFTER
