from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("AtomicCharge",)


class AtomicCharge(SimpleKeywordBox):
    """Enum to store all simple keywords of type AtomicCharge"""

    AIM = SimpleKeyword("aim")
    ALLPOP = SimpleKeyword("allpop")
    CHELPG = SimpleKeyword("chelpg")
    CHELPG_LARGE = SimpleKeyword("chelpg(large)")
    DENSITYANALYSIS = SimpleKeyword("densityanalysis")
    FMOPOP = SimpleKeyword("fmopop")
    FMOPOPULATIONS = SimpleKeyword("fmopopulations")
    HIRSHFELD = SimpleKeyword("hirshfeld")
    LOEWDIN = SimpleKeyword("loewdin")
    MAYER = SimpleKeyword("mayer")
    MBIS = SimpleKeyword("mbis")
    MULLIKEN = SimpleKeyword("mulliken")
    NOAIM = SimpleKeyword("noaim")
    NOFMOPOP = SimpleKeyword("nofmopop")
    NOFMOPOPULATIONS = SimpleKeyword("nofmopopulations")
    NOHIRSHFELD = SimpleKeyword("nohirshfeld")
    NOLOEWDIN = SimpleKeyword("noloewdin")
    NOMAYER = SimpleKeyword("nomayer")
    NOMBIS = SimpleKeyword("nombis")
    NOMULLIKEN = SimpleKeyword("nomulliken")
    NONPA = SimpleKeyword("nonpa")
    NOPOP = SimpleKeyword("nopop")
    NOREDUCEDPOP = SimpleKeyword("noreducedpop")
    NPA = SimpleKeyword("npa")
    REDUCEDPOP = SimpleKeyword("reducedpop")
