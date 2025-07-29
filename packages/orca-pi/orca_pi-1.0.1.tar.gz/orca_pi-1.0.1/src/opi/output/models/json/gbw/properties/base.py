from pydantic import StrictFloat, StrictStr

from opi.output.models.base.get_item import GetItem


class Base(GetItem):
    """
    Contains the information about the base of the atoms

    Attributes
    ----------
    coefficients: list[StrictFloat]
        Coefficients of the basis functions
    exponents: list[StrictFloat]
        Exponents of the Basis functions
    shell: StrictStr
        Shell of the Basis set
    """

    coefficients: list[StrictFloat] | None = None
    exponents: list[StrictFloat] | None = None
    shell: StrictStr | None = None
