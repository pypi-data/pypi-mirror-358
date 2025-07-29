from pydantic import StrictBool

from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictNonNegativeFloat,
    StrictPositiveFloat,
    StrictPositiveInt,
)


class MbisPopAnalysis(GetItem):
    """This class contains the information about the MIBS population analysis

    Attributes
    ----------
    natoms: PositiveInt
        Number of atoms
    atno: list[list[PositiveInt]]
        list with the Atom number according to the PSE
    thresh: PositiveFloat
        Threshold for printing orbitals
    niter: PositiveInt
        Number of iterations
    largeprint: StrictBool
        Has "Largeprint" been used
    densa: PositiveFloat
        Alpha densely
    densb: PositiveFloat
        Beta densely
    atomiccharges: list[list[StrictFloat]]
        list with atomic charges
    spin: list[list[StrictFloat]]
        list of the spin density
    npopval: list[list[NonNegativeFloat]]
        Population value of each atoms
    sigmaval: list[list[StrictFloat]]
        list of sigma value of the atoms
    """

    natoms: StrictPositiveInt | None = None
    atno: list[list[StrictPositiveInt]] | None = None
    thresh: StrictPositiveFloat | None = None
    niter: StrictPositiveInt | None = None
    largeprint: StrictBool | None = None
    densa: StrictPositiveFloat | None = None
    densb: StrictPositiveFloat | None = None
    atomiccharges: list[list[StrictFiniteFloat]] | None = None
    spin: list[list[StrictFiniteFloat]] | None = None
    npopval: list[list[StrictNonNegativeFloat]] | None = None
    sigmaval: list[list[StrictFiniteFloat]] | None = None
