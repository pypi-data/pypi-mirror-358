from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Dlpno",)


class Dlpno(SimpleKeywordBox):
    """Enum to store all simple keywords of type Dlpno"""

    HFLD = SimpleKeyword(
        "hfld"
    )  # HF + Dispersion energy decomposition  as cheaper alternative to DLPNO-CCSD(T) LED
    LED = SimpleKeyword("led")  # Energy decomposition for DLPNO-CCSD(T)
    LOOSEPNO = SimpleKeyword("loosepno")  # loose PNO settings
    NORMALPNO = SimpleKeyword("normalpno")  # normal PNO settings
    TIGHTPNO = SimpleKeyword("tightpno")  # Tight PNO settings
    ADLD = SimpleKeyword("adld")
    PNOEXTRAPOLATION = SimpleKeyword("pnoextrapolation")  # automatic extrapolation of PNO space
