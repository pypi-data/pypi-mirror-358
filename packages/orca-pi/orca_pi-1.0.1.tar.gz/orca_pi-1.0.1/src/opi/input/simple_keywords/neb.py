from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Neb",)


class Neb(SimpleKeywordBox):
    """Enum to store all simple keywords of type Neb"""

    NEB = SimpleKeyword("neb")  # NEB for finding minimal energy pathways (and transition states)
    NEB_CI = SimpleKeyword(
        "neb-ci"
    )  # NEB for finding minimal energy pathways (and transition states)
    NEB_IDPP = SimpleKeyword(
        "neb-idpp"
    )  # NEB for finding minimal energy pathways (and transition states)
    NEB_MMFTS = SimpleKeyword(
        "neb-mmfts"
    )  # NEB for finding minimal energy pathways (and transition states)
    NEB_TS = SimpleKeyword(
        "neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    FAST_NEB_TS = SimpleKeyword(
        "fast-neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    LOOSE_NEB_TS = SimpleKeyword(
        "loose-neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    TIGHT_NEB_TS = SimpleKeyword(
        "tight-neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    ZOOM_NEB = SimpleKeyword(
        "zoom-neb"
    )  # NEB for finding minimal energy pathways (and transition states)
    ZOOM_NEB_CI = SimpleKeyword(
        "zoom-neb-ci"
    )  # NEB for finding minimal energy pathways (and transition states)
    ZOOM_NEB_TS = SimpleKeyword(
        "zoom-neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    FLAT_NEB_TS = SimpleKeyword(
        "flat-neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    IRC = SimpleKeyword("irc")  # internal reaction coordinate
    SCANTS = SimpleKeyword("scants")  # scan for transition state
