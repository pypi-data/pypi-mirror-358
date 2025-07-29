from typing import Literal

from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictNonNegativeInt,
    StrictPositiveInt,
)
from opi.output.models.json.property.properties.energy import Energy


class MdciEnergies(Energy):
    """
    This class contains information about the MDCI energy calculation done after a SCF energy calculation

    Attributes
    ----------
    numofel: PositiveInt
        Number of electrons
    numofcorrel: StrictPositiveInt
        Number of corr-electrons
    numofalphacorrel: StrictNonNegativeInt
        Number of corr-electrons with an alpha spin
    numofbetacorell: StrictNonNegativeInt
        Number of corr-electrons with a beta spin
    refenergy: list[list[StrictFiniteFloat]]
        Energy reference
    correnergy: list[list[StrictFiniteFloat]]
        Total energy contribution of the electron-correlation
    aacorren: list[list[StrictFiniteFloat]]
        Energy contribution of the alpha alpha electron-correlation
    bbcorren: list[list[StrictFiniteFloat]]
        Energy contribution of the beta beta electron-correlation
    abcorren: list[list[StrictFiniteFloat]]
        Energy contribution of the alpha beta electron-correlation
    corrds: list[list[StrictFiniteFloat]]
        singlet pair energy of double amplitudes
    corrdt: list[list[StrictFiniteFloat]]
        Triplet pair energy of double amplitudes
    corrss: list[list[StrictFiniteFloat]]
        Singlet pair energy of quadratic single amplitudes
    corrst: list[list[StrictFiniteFloat]]
        Triplet pair energy of quadratic single amplitudes
    triplesenergy: list[list[StrictFiniteFloat]]
        Triplets correlation energy
    """

    numofel: StrictPositiveInt | None = None
    numofcorrel: StrictPositiveInt | None = None
    numofalphacorrel: StrictNonNegativeInt | None = None
    numofbetacorrel: StrictNonNegativeInt | None = None
    refenergy: list[list[StrictFiniteFloat]] | None = None
    correnergy: list[list[StrictFiniteFloat]] | None = None
    aacorren: list[list[StrictFiniteFloat]] | None = None
    bbcorren: list[list[StrictFiniteFloat]] | None = None
    abcorren: list[list[StrictFiniteFloat]] | None = None
    corrds: list[list[StrictFiniteFloat]] | None = None
    corrdt: list[list[StrictFiniteFloat]] | None = None
    corrss: list[list[StrictFiniteFloat]] | None = None
    corrst: list[list[StrictFiniteFloat]] | None = None
    triplesenergy: list[list[StrictFiniteFloat]] | None = None


# string for CCSD(T) / singles doubles and perturbative triples
class Mdcisd_t_Energies(MdciEnergies):
    method: Literal["MDCI(SD(T))"]


# string for CCSD / singles doubles
class MdcisdEnergies(MdciEnergies):
    method: Literal["MDCI(SD)"]
