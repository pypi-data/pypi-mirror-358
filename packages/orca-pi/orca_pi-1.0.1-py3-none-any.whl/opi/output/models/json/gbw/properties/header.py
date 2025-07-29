from pydantic import StrictStr

from opi.output.models.base.get_item import GetItem


class OrcaHeader(GetItem):
    """
    This class contains the information about the Orca Header

    Attributes
    ----------
    date: StrictStr
        Time and Date of the calculation
    git: StrictStr
        Git version
    version: StrictStr
        Orca-version
    """

    date: StrictStr | None = None
    git: StrictStr | None = None
    version: StrictStr | None = None
