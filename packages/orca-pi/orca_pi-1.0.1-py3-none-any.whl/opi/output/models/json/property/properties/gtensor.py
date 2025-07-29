from pydantic import StrictInt, StrictStr

from opi.output.models.base.get_item import GetItem
from opi.output.models.base.strict_types import (
    StrictFiniteFloat,
    StrictPositiveInt,
)


class Gtensor(GetItem):
    """
    This class contains information about the G-Tensor in EPR calculation

    Attributes
    ----------
    method: StrictStr
       Used method for this calculation
    level: StrictStr
        Type and relaxation of density
    mult : StrictPositiveInt
        Multiplicity of the electronic state
    state : StrictInt
        Electronic state
    irrep : StrictInt
        Irreducible representation of the electronic state
    g_matrix: list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]]
        Matrix of the G-Tensor
    g_elec: StrictFiniteFloat
        The free electron G-value contribution
    g_rmc: StrictFiniteFloat
        Reduced mass correction
    g_tot: list[list[StrictFiniteFloat]]
        Total G-tensor
    g_iso: StrictFiniteFloat
        Isotropic part of the G-tensor
    g_dso: list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]]
        Diamagnetic contribution to the G-tensor
    g_pso: list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]]
        Paramagnetic contribution to the G-tensor
    delta_g: list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]]
        Delta G-Tensor w.r.t the free electron
    delta_g_iso: StrictFiniteFloat
        Error of the isotropic part of the G-tensor
    orientation: list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]]
        Orientation of the G-tensor
    """

    method: StrictStr | None = None
    level: StrictStr | None = None
    mult: StrictPositiveInt | None = None
    state: StrictInt | None = None
    irrep: StrictInt | None = None
    g_matrix: list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]] | None = None
    g_elec: StrictFiniteFloat | None = None
    g_rmc: StrictFiniteFloat | None = None
    g_tot: list[list[StrictFiniteFloat]] | None = None
    g_iso: StrictFiniteFloat | None = None
    g_dso: list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]] | None = None
    g_pso: list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]] | None = None
    delta_g: list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]] | None = None
    delta_g_iso: StrictFiniteFloat | None = None
    orientation: list[tuple[StrictFiniteFloat, StrictFiniteFloat, StrictFiniteFloat]] | None = None
