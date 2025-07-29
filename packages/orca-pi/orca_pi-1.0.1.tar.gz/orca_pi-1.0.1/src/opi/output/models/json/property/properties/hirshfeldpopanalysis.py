from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictNonNegativeFloat,
    StrictPositiveInt,
)


class HirshfeldPopulationAnalysis(GetItem):
    """
    Has the Information about the Hirshfeld population analysis

    Attributes
    ----------
    natoms: StrictPositiveInt
        Numbers of atoms
    atno: list[list[StrictPositiveInt]]
        Atom number according to the position in the periodic table
    densa: StrictNonNegativeFiniteFloat
        Density of alpha electrons
    densb: StrictNonNegativeFiniteFloat
        Density of beta electrons
    atomiccharges: list[list[StrictFiniteFloat]]
        Total charges of the atoms according to the Hirshfeld population analysis
    spin: list[list[StrictFiniteFloat]]
        list of the spin densities, at the atoms
    """

    natoms: StrictPositiveInt | None = None
    atno: list[list[StrictPositiveInt]] | None = None
    densa: StrictNonNegativeFloat | None = None
    densb: StrictNonNegativeFloat | None = None
    atomiccharges: list[list[StrictFiniteFloat]] | None = None
    spin: list[list[StrictFiniteFloat]] | None = None
