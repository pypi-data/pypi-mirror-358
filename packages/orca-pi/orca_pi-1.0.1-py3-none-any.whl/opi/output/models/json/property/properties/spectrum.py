from pydantic import StrictBool, StrictStr

from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictNonNegativeFloat,
    StrictNonNegativeInt,
    StrictPositiveFloat,
    StrictPositiveInt,
)


class Spectrum(GetItem):
    """
    This class contains the information about calculated spectra like UVVis or ECD spectra

    Attributes
    ----------
    density_name: StrictStr
        Name of property with used theory
    temperature: StrictNonNegativeFloat
        Assumed temperature in the calculation
    method: StrictPositiveInt
        Method used in this calculation
    relcorrection: StrictPositiveInt
        Type of relativistic treatment in quasi degenerate perturbation theory in this calculation
    denstype: StrictNonNegativeInt
        Used density type in this calculation
    deritype: StrictNonNegativeInt
        Type of derived used in this calculation
    denslevel: StrictNonNegativeInt
        Source of density
    representation: StrictStr
        Used representation (passible Unknown, Length, Velocity)
    pointgroup: StrictStr
        Pointgroup of the molecule
    ntrans: StrictNonNegativeInt
        Number of transition states modeled in the calculation
    dohighermoments: StrictBool
        Are higher moments supposed to be used
    states: list[tuple[StrictNonNegativeInt, StrictNonNegativeInt, StrictPositiveInt, StrictNonNegativeInt]]
        Contains the initial and final states
    multiplicities: list[tuple[StrictPositiveFloat, StrictPositiveFloat]]
        Contains the multiplicity of the initial and final state
    excitationenergies: list[list[StrictFiniteFloat]]
        Contains the excitation energies for all modeled transition
    """

    density_name: StrictStr | None = None
    temperature: StrictNonNegativeFloat | None = None
    method: StrictPositiveInt | None = None
    relcorrection: StrictPositiveInt | None = None
    denstype: StrictNonNegativeInt | None = None
    deritype: StrictNonNegativeInt | None = None
    denslevel: StrictNonNegativeInt | None = None
    representation: StrictStr | None = None
    pointgroup: StrictStr | None = None
    ntrans: StrictNonNegativeInt | None = None
    dohighermoments: StrictBool | None = None
    states: (
        list[
            tuple[
                StrictNonNegativeInt,
                StrictNonNegativeInt,
                StrictPositiveInt,
                StrictNonNegativeInt,
            ]
        ]
        | None
    ) = None
    multiplicities: list[tuple[StrictPositiveFloat, StrictPositiveFloat]] | None = None
    excitationenergies: list[list[StrictFiniteFloat]] | None = None
