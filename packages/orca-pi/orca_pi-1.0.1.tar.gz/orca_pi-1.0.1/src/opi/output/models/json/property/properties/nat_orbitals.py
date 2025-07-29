from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictNonNegativeInt,
)


class NaturalOrbitals(GetItem):
    """
    This class contains the information about the natural orbitals in a broken symmetry calculation

    Attributes
    ----------
    nel: StrictNonNegativeInt
        Number of electrons
    nsomo: StrictNonNegativeInt
        Number of SOMO
    ndomo: StrictNonNegativeInt
        Number of DOMO
    nvmo: StrictNonNegativeInt
        Number of Virtual MO
    nnatoorbs: StrictNonNegativeInt
        Number of natural orbitals
    occuno: list[list[StrictFloat]]
        Number of occupation
    occunso: list[list[StrictFiniteFloat]]
        Number of occupation SO
    """

    nel: StrictNonNegativeInt | None = None
    nsomo: StrictNonNegativeInt | None = None
    ndomo: StrictNonNegativeInt | None = None
    nvmo: StrictNonNegativeInt | None = None
    nnatoorbs: StrictNonNegativeInt | None = None
    occuno: list[list[StrictFiniteFloat]] | None = None
    occunso: list[list[StrictFiniteFloat]] | None = None
