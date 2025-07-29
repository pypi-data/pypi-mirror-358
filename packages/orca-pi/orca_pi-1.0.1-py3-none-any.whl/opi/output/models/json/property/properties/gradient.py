from pydantic import StrictInt, StrictStr

from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictNonNegativeFloat,
    StrictPositiveInt,
)


class NucGradient(GetItem):
    """
    This class contains information about the SCF nuclear gradients

    Attributes
    ----------
    natoms: StrictPositiveInt
        Number of atoms in the calculation
    method : StrictStr
        Underlying electronic structure method
    level : StrictStr
        Source of density e.g. linearized, un-relaxed, relaxed
    mult : StrictPositiveInt
        Multiplicity of the electronic state
    state : StrictInt
        Electronic state
    irrep : StrictInt
        Irreducible representation of the electronic state
    gradnorm: StrictNonNegativeFiniteFloat
        Total norm of all gradients
    grad: list[list[StrictFiniteFloat]]
        Gradient for each atom in each dimension
    """

    natoms: StrictPositiveInt | None = None
    method: StrictStr | None = None
    level: StrictStr | None = None
    mult: StrictPositiveInt | None = None
    state: StrictInt | None = None
    irrep: StrictInt | None = None
    gradnorm: StrictNonNegativeFloat | None = None
    grad: list[list[StrictFiniteFloat]] | None = None
