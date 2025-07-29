from pydantic import StrictInt, StrictStr

from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictNonNegativeFloat,
    StrictPositiveFloat,
    StrictPositiveInt,
)


class Tensor(GetItem):
    """
    This class contains the A-Tensors of the epr calculation

    Attributes
    ----------
    method: StrictStr
        Used method in this calculation
    level: StrictStr
        Type and relaxation of density
    mult : StrictPositiveInt
        Multiplicity of the electronic state
    state : int
        Electronic state
    irrep : int
        Irreducible representation of the electronic state
    numofnucs: StrictPositiveInt
        Number of calculated nuclei
    nuc: list[StrictPositiveInt]
        list of used nuclei
    elem: list[StrictPositiveInt]
        Atomic number of the nucleus
    isotope: list[StrictPositiveFloat]
        Used isotope of the element
    i: list[StrictNonNegativeFloat]
        Spin of nucleus
    pfac: list[StrictPositiveFloat]
        Prefactor in MHz
    araw: list[list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]]]
        Raw tensors of each tensor
    aeigenvalues: list[list[list[StrictFiniteFloat]]]
        Eigenvalue of each tensor
    aiso: list[StrictFiniteFloat]
        Iso value of each tensor
    orientation: list[list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]]]
        Eigenvectors of each tensor
    """

    method: StrictStr | None = None
    level: StrictStr | None = None
    mult: StrictPositiveInt | None = None
    state: StrictInt | None = None
    irrep: StrictInt | None = None
    numofnucs: StrictPositiveInt | None = None
    nuc: list[StrictPositiveInt] | None = None
    elem: list[StrictPositiveInt] | None = None
    isotope: list[StrictPositiveFloat] | None = None
    i: list[StrictNonNegativeFloat] | None = None
    pfac: list[StrictPositiveFloat] | None = None
    araw: list[list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]]] | None = None
    aeigenvalues: list[list[list[StrictFiniteFloat]]] | None = None
    aiso: list[StrictFiniteFloat] | None = None
    orientation: (
        list[list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]]] | None
    ) = None
