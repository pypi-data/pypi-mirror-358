from pydantic import Field, StrictInt

from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictPositiveInt,
)


class TdDft(GetItem):
    """
    This class contains the information about the TD-DFT

    Attributes
    ----------
    iroot: StrictInt
        The root to be optimized
    orbwin: list[StrictPositiveInt]
        Orbital Window
    x: StrictNonNegativeFloat
        AO basis amplitudes for cis/tda-td-dft
    xy: StrictNonNegativeFloat
        AO basis amplitudes for rpa/td-dft
    """

    iroot: StrictInt | None = None
    orbwin: list[StrictPositiveInt] | None = None
    x: list[StrictFiniteFloat] | None = None
    xy: list[StrictFiniteFloat] | None = Field(default=None, alias="x+y")
