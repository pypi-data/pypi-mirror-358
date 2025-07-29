from pydantic import StrictStr

from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictPositiveFloat,
    StrictPositiveInt,
)


class SolvDetails(GetItem):
    """
    This class contains information about the solvation Calculation

    Attributes
    ---------
    solvent: StrictStr
        Name of the solvent
    epsilon: StrictPositiveFloat
        Dielectric constant of the solvent
    refrac: StrictPositiveFloat
        Refraction index of the solvent
    rsolv: StrictPositiveFloat
        Radiation of the solvent
    surfacetype: StrictStr
        Type of the solvation surface
    npoints: StrictPositiveInt
        Number of points
    surfacearea: StrictPositiveFloat
        Surface area
    cpcmdielenergy: StricFinitetFloat
        Total solvation energy
    """

    solvent: StrictStr | None = None
    epsilon: StrictPositiveFloat | None = None
    refrac: StrictPositiveFloat | None = None
    rsolv: StrictPositiveFloat | None = None
    surfacetype: StrictStr | None = None
    npoints: StrictPositiveInt | None = None
    surfacearea: StrictPositiveFloat | None = None
    cpcmdielenergy: StrictFiniteFloat | None = None
