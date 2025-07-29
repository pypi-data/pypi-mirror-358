from typing import Literal

from opi.output.models.base.strict_types import StrictNonNegativeInt
from opi.output.models.json.property.properties.energy import Energy


class CisEnergy(Energy):
    """
    Has the Information about energies that were calculated in the ORCA job

    Attributes
    ----------
    method: Literal["TDA/CIS"]
    String that identifies the method that was used for the energy calculation.
    Is used for identifying different energy types
    block: list[list[StrictNonNegativeInt]]
    nblocks: StrictNonNegativeInt
    nroots: list[list[StrictNonNegativeInt]]
    ntotalroots: StrictNonNegativeInt
    relcorr: str
    root: list[list[StrictNonNegativeInt]]
    dcorr: float
        (D) correction algorithm
    e0: float
        Energy of the ground state
    mode: str
    multp1: bool
        if the higher multiplicity was also done
    """

    method: Literal["TDA/CIS"]
    block: list[list[StrictNonNegativeInt]]
    nblocks: StrictNonNegativeInt
    nroots: list[list[StrictNonNegativeInt]]
    ntotalroots: StrictNonNegativeInt
    relcorr: str
    root: list[list[StrictNonNegativeInt]]
    dcorr: float
    e0: float
    mode: str
    multp1: bool
