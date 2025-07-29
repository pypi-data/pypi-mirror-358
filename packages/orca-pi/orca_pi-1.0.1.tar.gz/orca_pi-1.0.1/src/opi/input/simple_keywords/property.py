from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Property",)


class Property(SimpleKeywordBox):
    """Enum to store all simple keywords of type Property"""

    NMR = SimpleKeyword("nmr")  # Calculate NMR parameters
    G_TENSOR = SimpleKeyword("g-tensor")  # Calculate EPR parameters
    UCO = SimpleKeyword("uco")
    NOUCO = SimpleKeyword("nouco")
    UNO = SimpleKeyword("uno")
    NOUNO = SimpleKeyword("nouno")
    NBO = SimpleKeyword("nbo")
    NONBO = SimpleKeyword("nonbo")
