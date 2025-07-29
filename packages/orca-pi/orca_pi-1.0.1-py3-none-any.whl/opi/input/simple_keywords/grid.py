from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Grid",)


class Grid(SimpleKeywordBox):
    """Enum to store all simple keywords of type Grid"""

    DEFGRID1 = SimpleKeyword("defgrid1")  # small grid
    DEFGRID2 = SimpleKeyword("defgrid2")  # medium grid
    DEFGRID3 = SimpleKeyword("defgrid3")  # large grid
    REFGRID = SimpleKeyword("refgrid")  # reference grid
    ROTINVGRID = SimpleKeyword("rotinvgrid")  # Rotational invariant grid
