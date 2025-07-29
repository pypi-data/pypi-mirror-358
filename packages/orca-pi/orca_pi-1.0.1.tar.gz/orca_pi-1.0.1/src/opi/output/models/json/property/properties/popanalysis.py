from pydantic import StrictInt, StrictStr

from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictNonNegativeInt,
    StrictPositiveInt,
)


class PopulationAnalysis(GetItem):
    """
    Has the Information about the different population analysis

    Attributes
    ----------
    natoms: StrictPositiveInt
        Numbers of atoms
    atno : list[list[StrictPositiveInt]]
        Atom-number according to the position in the periodic table
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
    atomiccharges: list[list[StrictFiniteFloat]]
        Charges of the atoms according to the population analysis
    """

    natoms: StrictPositiveInt | None = None
    atno: list[list[StrictNonNegativeInt]] | None = None
    method: StrictStr | None = None
    level: StrictStr | None = None
    mult: StrictPositiveInt | None = None
    state: StrictInt | None = None
    irrep: StrictInt | None = None
    atomiccharges: list[list[StrictFiniteFloat]] | None = None
