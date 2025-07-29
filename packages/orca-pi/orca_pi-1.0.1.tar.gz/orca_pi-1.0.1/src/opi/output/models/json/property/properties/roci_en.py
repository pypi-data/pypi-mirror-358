from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictPositiveInt,
)


class RoCiEnergy(GetItem):
    """
    This class contains infos about the restricted open shell CI energies

    Attributes
    ----------
    multiplicities: list[list[StrictPositiveFloat]]
        list of the multiplicities of the states
    energies: list[Lis[StrictFiniteFloat]]
        Energies of the stats
    refenergy: StrictFiniteFloat
        Reference energy
    correnergy: StrictFiniteFloat
        Correlation energy
    totalenergy: StrictFiniteFloat
        Total energy
    """

    multiplicities: list[list[StrictPositiveInt]] | None = None
    energies: list[list[StrictFiniteFloat]] | None = None
    refenergy: StrictFiniteFloat | None = None
    correnergy: StrictFiniteFloat | None = None
    totalenergy: StrictFiniteFloat | None = None
