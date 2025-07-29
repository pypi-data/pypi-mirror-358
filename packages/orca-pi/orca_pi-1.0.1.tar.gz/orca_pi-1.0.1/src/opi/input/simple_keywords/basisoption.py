from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("BasisOption",)


class BasisOption(SimpleKeywordBox):
    """Enum to store all simple keywords of type BasisOption"""

    ANOBASIS = SimpleKeyword("anobasis")  # Modifies a selected basis
    DECONTRACT = SimpleKeyword("decontract")  # Modifies a selected basis
    DECONTRACTAUX = SimpleKeyword("decontractaux")  # Modifies a selected basis
    DECONTRACTAUXC = SimpleKeyword("decontractauxc")  # Modifies a selected basis
    DECONTRACTAUXJ = SimpleKeyword("decontractauxj")  # Modifies a selected basis
    DECONTRACTAUXJK = SimpleKeyword("decontractauxjk")  # Modifies a selected basis
    DECONTRACTBAS = SimpleKeyword("decontractbas")  # Modifies a selected basis
    DECONTRACTCABS = SimpleKeyword("decontractcabs")  # Modifies a selected basis
    NOANOBASIS = SimpleKeyword("noanobasis")  # Modifies a selected basis
    NODECONTRACT = SimpleKeyword("nodecontract")  # Modifies a selected basis
    NODECONTRACTAUX = SimpleKeyword("nodecontractaux")  # Modifies a selected basis
    NODECONTRACTAUXC = SimpleKeyword("nodecontractauxc")  # Modifies a selected basis
    NODECONTRACTAUXJ = SimpleKeyword("nodecontractauxj")  # Modifies a selected basis
    NODECONTRACTAUXJK = SimpleKeyword("nodecontractauxjk")  # Modifies a selected basis
    NODECONTRACTBAS = SimpleKeyword("nodecontractbas")  # Modifies a selected basis
    NODECONTRACTCABS = SimpleKeyword("nodecontractcabs")  # Modifies a selected basis
    NOUNCONTRACT = SimpleKeyword("nouncontract")  # Modifies a selected basis
    NOUNCONTRACTAUX = SimpleKeyword("nouncontractaux")  # Modifies a selected basis
    NOUNCONTRACTAUXC = SimpleKeyword("nouncontractauxc")  # Modifies a selected basis
    NOUNCONTRACTAUXJ = SimpleKeyword("nouncontractauxj")  # Modifies a selected basis
    NOUNCONTRACTAUXJK = SimpleKeyword("nouncontractauxjk")  # Modifies a selected basis
    NOUNCONTRACTBAS = SimpleKeyword("nouncontractbas")  # Modifies a selected basis
    NOUNCONTRACTCABS = SimpleKeyword("nouncontractcabs")  # Modifies a selected basis
    UNCONTRACT = SimpleKeyword("uncontract")  # Modifies a selected basis
    UNCONTRACTAUX = SimpleKeyword("uncontractaux")  # Modifies a selected basis
    UNCONTRACTAUXC = SimpleKeyword("uncontractauxc")  # Modifies a selected basis
    UNCONTRACTAUXJ = SimpleKeyword("uncontractauxj")  # Modifies a selected basis
    UNCONTRACTAUXJK = SimpleKeyword("uncontractauxjk")  # Modifies a selected basis
    UNCONTRACTBAS = SimpleKeyword("uncontractbas")  # Modifies a selected basis
    UNCONTRACTCABS = SimpleKeyword("uncontractcabs")  # Modifies a selected basis
