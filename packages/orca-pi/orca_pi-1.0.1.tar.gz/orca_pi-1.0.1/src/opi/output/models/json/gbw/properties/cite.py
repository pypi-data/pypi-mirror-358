from opi.output.models.base.get_item import GetItem
from opi.output.models.json.gbw.properties.paper import Paper


class Cite(GetItem):
    """
    This class contains the keys for the papers that are necessary to cite

    Attributes
    ----------
    ORCA2022: Paper | None, default None
        Key for the ORCA 2022 paper
    SHARK: Paper | None, default None
        Key for the SHARK paper
    """

    ORCA2022: Paper | None = None
    SHARK: Paper | None = None
