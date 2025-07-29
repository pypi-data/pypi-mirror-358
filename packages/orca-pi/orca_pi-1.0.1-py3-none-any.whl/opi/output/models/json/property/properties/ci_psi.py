from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictNonNegativeInt,
    StrictPositiveInt,
)


class CiPsi(GetItem):
    """
    This class contains the information about the CI PSI calculation

    Attributes
    ----------
    multiplicity: StrictPositiveInt
        Multiplicity of the system
    finalenergy: StrictFiniteFloat
        Final calculated energies
    numofroots: StrictNonNegativeInt
        Number of roots
    energies: list[list[StrictFiniteFloat]]
        list of calculated energies
    """

    multiplicity: StrictPositiveInt | None = None
    finalenergy: StrictFiniteFloat | None = None
    numofroots: StrictNonNegativeInt | None = None
    energies: list[list[StrictFiniteFloat]] | None = None
