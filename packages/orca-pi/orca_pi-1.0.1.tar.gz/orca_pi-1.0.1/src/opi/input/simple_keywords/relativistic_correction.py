from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("RelativisticCorrection",)


class RelativisticCorrection(SimpleKeywordBox):
    """Enum to store all simple keywords of type RelativisticCorrection"""

    AMFI = SimpleKeyword("amfi")
    DBOC = SimpleKeyword("dboc")
    DKH = SimpleKeyword("dkh")
    DKH1 = SimpleKeyword("dkh1")
    DKH2 = SimpleKeyword("dkh2")
    DLU_X2C = SimpleKeyword("dlu-x2c")
    IORA = SimpleKeyword("iora")
    IORA_RI = SimpleKeyword("iora/ri")
    IORAMM_RI = SimpleKeyword("ioramm/ri")
    NESC = SimpleKeyword("nesc")
    NODBOC = SimpleKeyword("nodboc")
    NOSOCENERGY = SimpleKeyword("nosocenergy")
    REL1C = SimpleKeyword("rel1c")
    RELDLU = SimpleKeyword("reldlu")
    RELFULL = SimpleKeyword("relfull")
    RI_SOMF = SimpleKeyword("ri-somf")
    RI_SOMF_1X = SimpleKeyword("ri-somf(1x)")
    RI_SOMF_4X = SimpleKeyword("ri-somf(4x)")
    RI_SOMF_4XS = SimpleKeyword("ri-somf(4xs)")
    SOCENERGY = SimpleKeyword("socenergy")
    SOMF = SimpleKeyword("somf")
    SOMF_1X = SimpleKeyword("somf(1x)")
    SOMF_4X = SimpleKeyword("somf(4x)")
    SOMF_4XS = SimpleKeyword("somf(4xs)")
    VEFF_SOC = SimpleKeyword("veff-soc")
    VEFF_2X_SOC = SimpleKeyword("veff(-2x)-soc")
    X2C = SimpleKeyword("x2c")
    ZEFF_SOC = SimpleKeyword("zeff-soc")
    ZORA = SimpleKeyword("zora")
    ZORA_RI = SimpleKeyword("zora/ri")
