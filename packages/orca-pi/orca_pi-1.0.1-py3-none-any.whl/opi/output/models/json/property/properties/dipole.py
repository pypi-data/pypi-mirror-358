from pydantic import StrictBool, StrictInt, StrictStr

from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictNonNegativeFloat,
    StrictPositiveInt,
)


class Dipole(GetItem):
    """
    Has the Information about the dipole-Moment calculated by the ORCA Job

    Attributes
    ----------
    method: StrictStr
        Used method: SCF, DFT, CC or similar
    level: StrictStr
        Typ and relaxation of the density
    mult: StrictPositiveInt
        Multiplicity of the molecule
    state : StrictInt
        Electronic state
    irrep : StrictInt
        Irreducible representation of the electronic state
    doatomicdipole: StrictBool
        Should the dipole atom calculation be done
    dipoleeleccontrib: list[list[StrictFiniteFloat]]
        Contribution of the electrons on the dipole moment in all three dimension
    dipolenuccontrib: list[list[StrictFiniteFloat]]
        Contribution of the nucleus on the dipole moment in all three dimension
    dipolemagnitude: StrictNonNegativeFloat
        Float absolute dipole moment independent of direction
    dipoletotal: list[list[StrictFiniteFloat]]
        Total dipole moment in all three dimension
    """

    method: StrictStr | None = None
    level: StrictStr | None = None
    mult: StrictPositiveInt | None = None
    state: StrictInt | None = None
    irrep: StrictInt | None = None
    doatomicdipole: StrictBool | None = None
    dipoleeleccontrib: list[list[StrictFiniteFloat]] | None = None
    dipolenuccontrib: list[list[StrictFiniteFloat]] | None = None
    dipolemagnitude: StrictNonNegativeFloat | None = None
    dipoletotal: list[list[StrictFiniteFloat]] | None = None
