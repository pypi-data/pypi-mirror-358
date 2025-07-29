from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("ShellType",)


class ShellType(SimpleKeywordBox):
    """Enum to store all simple keywords of type ShellType"""

    RHF = SimpleKeyword("rhf")  # Type of the wavefunction: restricted, unrestricted, multireference
    RKS = SimpleKeyword("rks")  # Type of the wavefunction: restricted, unrestricted, multireference
    ROHF = SimpleKeyword(
        "rohf"
    )  # Type of the wavefunction: restricted, unrestricted, multireference
    ROKS = SimpleKeyword(
        "roks"
    )  # Type of the wavefunction: restricted, unrestricted, multireference
    UHF = SimpleKeyword("uhf")  # Type of the wavefunction: restricted, unrestricted, multireference
    UKS = SimpleKeyword("uks")  # Type of the wavefunction: restricted, unrestricted, multireference
    CASSCF = SimpleKeyword(
        "casscf"
    )  # Type of the wavefunction: restricted, unrestricted, multireference
