from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("DispersionCorrection",)


class DispersionCorrection(SimpleKeywordBox):
    """Enum to store all simple keywords of type DispersionCorrection"""

    ABC = SimpleKeyword("abc")  # three body term for d3bj
    D2 = SimpleKeyword("d2")  # D2
    D3 = SimpleKeyword("d3")  # D3
    D3ZERO = SimpleKeyword("d3zero")  # D3 Zero damping
    D3BJ = SimpleKeyword("d3bj")  # D3 with BJ damping
    D3TZ = SimpleKeyword("d3tz")  # Use TZ optimized values damping parameters if available
    D4 = SimpleKeyword("d4")  # Use D4 dispersion correction
    NL = SimpleKeyword("nl")  # use -NL / -VV10 / -V dispersion correction
    POPDISP = SimpleKeyword("popdisp")  # pairwise dispersion correction analysis
    SCNL = SimpleKeyword("scnl")  # Use self-consistent nl
