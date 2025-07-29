from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Goat",)


class Goat(SimpleKeywordBox):
    """Enum to store all simple keywords of type Goat"""

    GOAT = SimpleKeyword("goat")  # GOAT Methods
    GOAT_COARSE = SimpleKeyword("goat-coarse")  # GOAT Methods
    GOAT_DIVERSITY = SimpleKeyword("goat-diversity")  # GOAT Methods
    GOAT_ENTROPY = SimpleKeyword("goat-entropy")  # GOAT Methods
    GOAT_EXPLORE = SimpleKeyword("goat-explore")  # GOAT Methods
    GOAT_REACT = SimpleKeyword("goat-react")  # GOAT Methods
    GOAT_TS = SimpleKeyword("goat-ts")  # GOAT Methods
