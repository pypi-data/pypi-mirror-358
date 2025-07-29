from pydantic import StrictBool

from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictNonNegativeFloat,
    StrictNonNegativeInt,
    StrictPositiveFloat,
)


class ThermochemistryEnergy(GetItem):
    """
    This class contains information about the thermochemistry and energies calculated in the calculation

    Attributes
    ----------
    temperature: StrictNonNegativeFloat
        The temperature simulated in the calculation
    pressure: StrictNonNegativeFloat
       The pressure simulated in the calculation
    totalmass: StrictPositiveFloat
       The total mass of the molecule(s)
    spindegeneracy: StrictNonNegativeInt
        Degeneracy of the spin
    elenergy: StrictFiniteFloat
        Electron energy
    transenergy: StrictFiniteFloat
        Energy of the transition
    rotenergy: StrictFiniteFloat
        Energy of the rotation
    vibenergy: StrictFiniteFloat
        Energy of the vibration
    freqscalingfactor: StrictPositiveFloat
        Scaling factor of the frequencies
    freq: list[list[StrictFiniteFloat]]
        list of all frequencies
    zpe: StrictPositiveFloat
        Zero point energy
    innerenergyu: StrictFiniteFloat
        Inner Energy of the system
    enthalpyh: StrictFiniteFloat
        Enthalpy of the system
    qel: StrictFiniteFloat
        Gibbs electron energy
    qrot: StrictNonNegativeFloat
        Gibbs energy for Rotations
    qvib: StrictNonNegativeFloat
        Gibbs energy for vibration
    entropys: StrictFiniteFloat
        Entropy of the system
    freeenergyg: StrictFiniteFloat
        Gibbs (free) energy of the system
    islinear: StrictBool
        Is the molecular linear (true), else false
    """

    temperature: StrictNonNegativeFloat | None = None
    pressure: StrictNonNegativeFloat | None = None
    totalmass: StrictPositiveFloat | None = None
    spindegeneracy: StrictNonNegativeInt | None = None
    elenergy: StrictFiniteFloat | None = None
    transenergy: StrictFiniteFloat | None = None
    rotenergy: StrictFiniteFloat | None = None
    vibenergy: StrictFiniteFloat | None = None
    numoffreqs: StrictNonNegativeInt | None = None
    freqscalingfactor: StrictPositiveFloat | None = None
    freq: list[list[StrictFiniteFloat]] | None = None
    zpe: StrictPositiveFloat | None = None
    innerenergyu: StrictFiniteFloat | None = None
    enthalpyh: StrictFiniteFloat | None = None
    qel: StrictFiniteFloat | None = None
    qrot: StrictNonNegativeFloat | None = None
    qvib: StrictNonNegativeFloat | None = None
    entropys: StrictFiniteFloat | None = None
    freeenergyg: StrictFiniteFloat | None = None
    islinear: StrictBool | None = None
