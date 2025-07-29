from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Avas",)


class Avas(SimpleKeywordBox):
    """Enum to store all simple keywords of type Avas"""

    AVAS_DOUBLE_D = SimpleKeyword("avas(double-d)")  # CASSCF initial guess
    AVAS_DOUBLE_DS = SimpleKeyword("avas(double-ds)")  # CASSCF initial guess
    AVAS_DOUBLE_F = SimpleKeyword("avas(double-f)")  # CASSCF initial guess
    AVAS_VALENCE_D = SimpleKeyword("avas(valence-d)")  # CASSCF initial guess
    AVAS_VALENCE_DS = SimpleKeyword("avas(valence-ds)")  # CASSCF initial guess
    AVAS_VALENCE_F = SimpleKeyword("avas(valence-f)")  # CASSCF initial guess
