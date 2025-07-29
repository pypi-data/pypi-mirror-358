from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Ecp",)


class Ecp(SimpleKeywordBox):
    """Enum to store all simple keywords of type Ecp"""

    CRENBL_ECP = SimpleKeyword("crenbl-ecp")  # effective core potentials
    DEFECP = SimpleKeyword("defecp")  # effective core potentials
    DEF2ECP = SimpleKeyword("def2ecp")  # effective core potentials
    DEF2_SD = SimpleKeyword("def2-sd")  # effective core potentials
    DHF_ECP = SimpleKeyword("dhf-ecp")  # effective core potentials
    DHFECP = SimpleKeyword("dhfecp")  # effective core potentials
    HAYWADT = SimpleKeyword("haywadt")  # effective core potentials
    LANL1 = SimpleKeyword("lanl1")  # effective core potentials
    LANL2 = SimpleKeyword("lanl2")  # effective core potentials
    SDD = SimpleKeyword("sdd")  # effective core potentials
    SK_MCDHF_RSC = SimpleKeyword("sk-mcdhf-rsc")  # effective core potentials
    VDZP_ECP = SimpleKeyword("vdzp-ecp")  # effective core potentials
    DEF2ECP_DEFECP_R2SCAN3C = SimpleKeyword(
        "def2ecp/defecp/r2scan3c"
    )  # effective core potentials (for r²SCAN-3c)s
