from enum import Enum, auto


class Rating(Enum):
    UNKNOWN = U = auto()
    GENERAL = G = auto()
    SENSITIVE = S = auto()
    QUESTIONABLE = Q = auto()
    EXPLICIT = E = auto()


class IllustType(Enum):
    ILLUST = auto()
    UGOIRA = auto()
    UNKNOWN = auto()


class IllustSize(Enum):
    MEDIUM = auto()
    LARGE = auto()
    ORIGINAL = auto()