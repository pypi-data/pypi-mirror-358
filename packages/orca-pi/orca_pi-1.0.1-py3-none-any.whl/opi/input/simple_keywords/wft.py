from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Wft",)


class Wft(SimpleKeywordBox):
    """Enum to store all simple keywords of type Wft"""

    HF = SimpleKeyword("hf")  # Hartee-Fock
    HF_3C = SimpleKeyword("hf-3c")  # 3c methods, do not require dispersion correction or basis set
    MP2 = SimpleKeyword("mp2")  # WFT Methods
    RIMP2 = SimpleKeyword("rimp2")  # WFT Methods
    OO_RI_MP2 = SimpleKeyword("oo-ri-mp2")  # WFT Methods
    SCS_MP2 = SimpleKeyword("scs-mp2")  # WFT Methods
    SOS_MP2 = SimpleKeyword("sos-mp2")  # WFT Methods
    DLPNO_MP2 = SimpleKeyword("dlpno-mp2")  # WFT Methods
    DLPNO_SCS_MP2 = SimpleKeyword("dlpno-scs-mp2")  # WFT Methods
    DLPNO_SOS_MP2 = SimpleKeyword("dlpno-sos-mp2")  # WFT Methods
    DLPNO_MP2_F12 = SimpleKeyword("dlpno-mp2-f12")  # WFT Methods
    DLPNO_MP2_F12D = SimpleKeyword("dlpno-mp2-f12d")  # WFT Methods
    MP3 = SimpleKeyword("mp3")  # WFT Methods
    SCS_MP3 = SimpleKeyword("scs-mp3")  # WFT Methods
    CCSD = SimpleKeyword("ccsd")  # WFT Methods
    CCSD_F12 = SimpleKeyword("ccsd-f12")  # WFT Methods
    DLPNO_CCSD = SimpleKeyword("dlpno-ccsd")  # WFT Methods
    DLPNO_CCSD_F12 = SimpleKeyword("dlpno-ccsd-f12")  # WFT Methods
    DLPNO_CCSD_F12D = SimpleKeyword("dlpno-ccsd-f12d")  # WFT Methods
    CCSD_T = SimpleKeyword("ccsd(t)")  # WFT Methods
    CCSD_T_F12 = SimpleKeyword("ccsd(t)-f12")  # WFT Methods
    DLPNO_CCSD_T = SimpleKeyword("dlpno-ccsd(t)")  # WFT Methods
    DLPNO_CCSD_T1 = SimpleKeyword("dlpno-ccsd(t1)")  # WFT Methods
    DLPNO_CCSD_T_F12 = SimpleKeyword("dlpno-ccsd(t)-f12")  # WFT Methods
    DLPNO_CCSD_T_F12D = SimpleKeyword("dlpno-ccsd(t)-f12d")  # WFT Methods
    DLPNO_CCSD_T1_F12 = SimpleKeyword("dlpno-ccsd(t1)-f12")  # WFT Methods
    DLPNO_CCSD_T1_F12D = SimpleKeyword("dlpno-ccsd(t1)-f12d")  # WFT Methods
    CISD = SimpleKeyword("cisd")  # WFT Methods
    CISD_T = SimpleKeyword("cisd(t)")  # WFT Methods
    CC2 = SimpleKeyword("cc2")  # WFT Methods
    ADC2 = SimpleKeyword("adc2")  # WFT Methods
    EOM_CCSD = SimpleKeyword("eom-ccsd")  # WFT Methods
    DLPNO_CISD = SimpleKeyword("dlpno-cisd")  # WFT Methods
    STEOM_CCSD = SimpleKeyword("steom-ccsd")  # WFT Methods
    DLPNO_STEOM_CCSD = SimpleKeyword("dlpno-steom-ccsd")  # WFT Methods
    CASPT2 = SimpleKeyword("caspt2")  # WFT Methods
    CASPT2K = SimpleKeyword("caspt2k")  # WFT Methods
    NEVPT2 = SimpleKeyword("nevpt2")  # WFT Methods
    SC_NEVPT2 = SimpleKeyword("sc-nevpt2")  # WFT Methods
    DLPNO_NEVPT2 = SimpleKeyword("dlpno-nevpt2")  # WFT Methods
