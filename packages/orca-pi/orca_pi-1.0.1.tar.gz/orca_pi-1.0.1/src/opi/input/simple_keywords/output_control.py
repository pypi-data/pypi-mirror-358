from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("OutputControl",)


class OutputControl(SimpleKeywordBox):
    """Enum to store all simple keywords of type OutputControl"""

    MINIPRINT = SimpleKeyword("miniprint")
    SMALLPRINT = SimpleKeyword("smallprint")
    NORMALPRINT = SimpleKeyword("normalprint")
    LARGEPRINT = SimpleKeyword("largeprint")
    SCFSOLVERTIME = SimpleKeyword("scfsolvertime")
    PRINTGAP = SimpleKeyword("printgap")
    PRINTMOS = SimpleKeyword("printmos")
    PRINTBASIS = SimpleKeyword("printbasis")  # printbas
    GRIDPRINT = SimpleKeyword("gridprint")  # Print grid information
    WRITEONLYINITIALPROPFILE = SimpleKeyword(
        "writeonlyinitialpropfile"
    )  # Only write property file for first geometry
    NOMOPRINT = SimpleKeyword("nomoprint")
    NOPROPFILE = SimpleKeyword("nopropfile")  # Write no property file
    NOPRINTMOS = SimpleKeyword("noprintmos")
