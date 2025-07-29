from typing import Literal

from opi.output.models.json.property.properties.energy import Energy


class ScfEnergy(Energy):
    """
    Has the Information about energies that were calculated in the ORCA job

    Attributes
    ----------
    method: Literal["SCF"]
    String that identifies the method that was used for the energy calculation.
    Is used for identifying different energy types
    """

    method: Literal["SCF"]
