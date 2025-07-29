from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Esd",)


class Esd(SimpleKeywordBox):
    """Enum to store all simple keywords of type Esd"""

    ESD = SimpleKeyword("esd")  # Check for excited state dynamics calculation
    ESD_ABS = SimpleKeyword("esd(abs)")  # Check for excited state dynamics calculation
    ESD_CPF = SimpleKeyword("esd(cpf)")  # Check for excited state dynamics calculation
    ESD_CPP = SimpleKeyword("esd(cpp)")  # Check for excited state dynamics calculation
    ESD_ECD = SimpleKeyword("esd(ecd)")  # Check for excited state dynamics calculation
    ESD_FLUOR = SimpleKeyword("esd(fluor)")  # Check for excited state dynamics calculation
    ESD_IC = SimpleKeyword("esd(ic)")  # Check for excited state dynamics calculation
    ESD_ISC = SimpleKeyword("esd(isc)")  # Check for excited state dynamics calculation
    ESD_MCD = SimpleKeyword("esd(mcd)")  # Check for excited state dynamics calculation
    ESD_PHOSP = SimpleKeyword("esd(phosp)")  # Check for excited state dynamics calculation
    ESD_RR = SimpleKeyword("esd(rr)")  # Check for excited state dynamics calculation
    ESD_RRAMAN = SimpleKeyword("esd(rraman)")  # Check for excited state dynamics calculation
