from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Approximation",)


class Approximation(SimpleKeywordBox):
    """Enum to store all simple keywords of type Approximation"""

    CLUSTERALL = SimpleKeyword("clusterall")  # cluster all grids
    COSXCLUSTERALL = SimpleKeyword("cosxclusterall")  # cluster cosx grid
    COSJXC = SimpleKeyword("cosjxc")  # fast but blurry DFT
    FMM = SimpleKeyword("fmm")  # Use FFM approximation
    FROZENCORE = SimpleKeyword("frozencore")  # Frozen core approx. in correlated WFT
    NOFROZENCORE = SimpleKeyword("nofrozencore")  # do not use frozen core approximation
    RI_BUPO_J = SimpleKeyword("ri-bupo/j")  # Use BUPO
    NOBUPO = SimpleKeyword("nobupo")  # Do not use BUPO
    NOCOSX = SimpleKeyword("nocosx")  # Do not use cosx
    RCSINGLESFOCK = SimpleKeyword("rcsinglesfock")  # Use COSX for Fock like single terms in CC
    NORCSINGLESFOCK = SimpleKeyword(
        "norcsinglesfock"
    )  # Do not use COSX for Fock like single terms in CC
    RI = SimpleKeyword("ri")  # Use RI
    NORI = SimpleKeyword("nori")  # Do not use RI
    RIJCOSX = SimpleKeyword("rijcosx")  # Approximation for two-electron integrals
    NORIJCOSX = SimpleKeyword("norijcosx")  # Approximation for two-electron integrals
    RIJKSINGLESFOCK = SimpleKeyword("rijksinglesfock")  # Use RIJK for Fock like single terms in CC
    NORIJKSINGLESFOCK = SimpleKeyword(
        "norijksinglesfock"
    )  # Do not use RIJK for Fock like single terms in CC
    USESFITTING = SimpleKeyword("usesfitting")
    NOSFITTING = SimpleKeyword("nosfitting")  # Do not use overlap fitting in cosx
    SPLITJ = SimpleKeyword("splitj")  # Approximation for two-electron integrals
    SPLITRIJ = SimpleKeyword("splitrij")  # Approximation for two-electron integrals
    NOSPLITRIJ = SimpleKeyword("nosplitrij")  # Approximation for two-electron integrals
    RIAO = SimpleKeyword("riao")  # Approximation for two-electron integrals
    RICOSJ = SimpleKeyword("ricosj")  # Approximation for two-electron integrals
    RICOSJX = SimpleKeyword("ricosjx")  # Approximation for two-electron integrals
    RIJK = SimpleKeyword("rijk")  # Approximation for two-electron integrals
    RIJONX = SimpleKeyword("rijonx")  # Approximation for two-electron integrals
    RIJXC = SimpleKeyword("rijxc")  # Approximation for two-electron integrals
