from pydantic import StrictStr

from opi.output.models.base.get_item import GetItem


class Paper(GetItem):
    """
    This class contains the information about the minimum literature that needs to bee cited

    Attributes
    ----------
    author: list[StrictStr]
        Name of the Authors
    title: StrictStr
        Title of the paper
    journal: StrictStr
        Journal that published the paper
    year: StrictPositiveInt
        Year of the publication
    volume: StrictPositiveInt | None default = None
        Volume of the Journal
    number: StrictPositiveInt | None default = None
        number of the paper
    pages: StrictStr
        Number of pages
    doi: StrictStr
        Doi of the paper
    type: StrictStr
        Type of the literature
    """

    author: list[StrictStr] | None = None
    title: StrictStr | None = None
    journal: StrictStr | None = None
    year: StrictStr | None = None
    volume: StrictStr | None = None
    number: StrictStr | None = None
    pages: StrictStr | None = None
    doi: StrictStr | None = None
    type: StrictStr | None = None
