from enum import Enum

class ConstraintType(str, Enum):
    SOD = "separation_of_duty"
    TEMPORAL = "temporal"
    ATTRIBUTE = "attribute"
    CONTEXT = "context"

class AccessMode(str, Enum):
    DIRECT = "direct"       # n_rzbac
    INFERENTIAL = "inferential"  # i_rzbac
