from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictNonNegativeFloat,
)


class CalculationTiming(GetItem):
    """
    Has the Information about the calculation Timing

    Attributes
    ----------
    gstep: StrictNonNegativeFloat
        Time of geometry steps
    gtoint: StrictNonNegativeFloat
        Time of integral generation
    prop: StrictNonNegativeFloat
        Time of property generation
    scf: StrictNonNegativeFloat
        Time of solving the SCF
    scfgrad: StrictNonNegativeFloat
        Time of gradient calculation
    sum: StrictNonNegativeFloat
        Total time of the calculation
    """

    gstep: StrictNonNegativeFloat | None = None
    gtoint: StrictNonNegativeFloat | None = None
    prop: StrictNonNegativeFloat | None = None
    scf: StrictNonNegativeFloat | None = None
    scfgrad: StrictNonNegativeFloat | None = None
    sum: StrictNonNegativeFloat | None = None
