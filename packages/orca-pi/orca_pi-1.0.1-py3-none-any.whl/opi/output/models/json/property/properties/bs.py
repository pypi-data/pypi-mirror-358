from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictPositiveFloat,
)


class BrokenSym(GetItem):
    """
    This class contains the information about the broken symmetry calculation

    Attributes
    ----------
    enhighspin: StrictFiniteFloat
        Energy of the high spin case
    enbrokensym: StrictFiniteFloat
        Energy of the broken symmetry case
    shighspin: StrictPositiveFloat
        Spin of the high spin case
    s2highspin: StrictPositiveFloat
        s² of the high spin case
    s2brokensym: StrictPositiveFloat
        s² of the broken symmetry case
    """

    enhighspin: StrictFiniteFloat | None = None
    enbrokensym: StrictFiniteFloat | None = None
    shighspin: StrictPositiveFloat | None = None
    s2highspin: StrictPositiveFloat | None = None
    s2brokensym: StrictPositiveFloat | None = None
