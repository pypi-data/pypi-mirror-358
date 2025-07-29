from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import StrictFiniteFloat


class SinglePointData(GetItem):
    """
    Has the Information about single points in ORCA

    Attributes
    ----------
    converged: bool
        Whether the singlepoint calculation has converged
    finalenergy: StrictFiniteFloat
        The energy printed as `FINAL SINGLE POINT ENERGY` in the
        ORCA output
    """

    converged: bool | None = None
    finalenergy: StrictFiniteFloat | None = None
