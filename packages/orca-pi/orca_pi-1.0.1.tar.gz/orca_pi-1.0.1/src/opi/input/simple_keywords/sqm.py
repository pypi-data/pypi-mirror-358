from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Sqm",)


class Sqm(SimpleKeywordBox):
    """Enum to store all simple keywords of type Sqm"""

    AM1 = SimpleKeyword("am1")  # SQM: Semiempirical quantum mechanical methods
    GFN0_XTB = SimpleKeyword("gfn0-xtb")  # GFN0-xTB also known as XTB0
    GFN1_XTB = SimpleKeyword("gfn1-xtb")  # GFN1-xTB also known as GFN-xTB or XTB1
    GFN2_XTB = SimpleKeyword("gfn2-xtb")  # GFN1-xTB also known as XTB or XTB2
    MNDO = SimpleKeyword("mndo")  # SQM: Semiempirical quantum mechanical methods
    NATIVE_GFN1_XTB = SimpleKeyword(
        "native-gfn1-xtb"
    )  # SQM: Semiempirical quantum mechanical methods
    NATIVE_GFN2_XTB = SimpleKeyword(
        "native-gfn2-xtb"
    )  # SQM: Semiempirical quantum mechanical methods
    NDDO_1 = SimpleKeyword("nddo/1")  # SQM: Semiempirical quantum mechanical methods
    NDDO_2 = SimpleKeyword("nddo/2")  # SQM: Semiempirical quantum mechanical methods
    NDDO_MK = SimpleKeyword("nddo/mk")  # SQM: Semiempirical quantum mechanical methods
    NONOTCH = SimpleKeyword("nonotch")  # SQM: Semiempirical quantum mechanical methods
    NOTCH = SimpleKeyword("notch")  # SQM: Semiempirical quantum mechanical methods
    PM3 = SimpleKeyword("pm3")  # SQM: Semiempirical quantum mechanical methods
    ZINDO_1 = SimpleKeyword("zindo/1")  # SQM: Semiempirical quantum mechanical methods
    ZINDO_2 = SimpleKeyword("zindo/2")  # SQM: Semiempirical quantum mechanical methods
    ZINDO_S = SimpleKeyword("zindo/s")  # SQM: Semiempirical quantum mechanical methods
    ZNDDO_1 = SimpleKeyword("znddo/1")  # SQM: Semiempirical quantum mechanical methods
    ZNDDO_2 = SimpleKeyword("znddo/2")  # SQM: Semiempirical quantum mechanical methods
