from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Docker",)


class Docker(SimpleKeywordBox):
    """Enum to store all simple keywords of type Docker"""

    NORMALDOCK = SimpleKeyword("normaldock")  # Docker Methods
    COMPLETEDOCK = SimpleKeyword("completedock")  # Docker Methods
    DOCK_GFN_FF = SimpleKeyword("dock(gfn-ff)")  # Docker Methods
    DOCK_GFN0_XTB = SimpleKeyword("dock(gfn0-xtb)")  # Docker Methods
    DOCK_GFN1_XTB = SimpleKeyword("dock(gfn1-xtb)")  # Docker Methods
    DOCK_GFN2_XTB = SimpleKeyword("dock(gfn2-xtb)")  # Docker Methods
    DOCK_GFNFF = SimpleKeyword("dock(gfnff)")  # Docker Methods
    DOCK_XTB = SimpleKeyword("dock(xtb)")  # Docker Methods
    DOCK_XTB0 = SimpleKeyword("dock(xtb0)")  # Docker Methods
    DOCK_XTB1 = SimpleKeyword("dock(xtb1)")  # Docker Methods
    DOCKER = SimpleKeyword("docker")  # GOAT Methods
    DOCKER_GFN_FF = SimpleKeyword("docker(gfn-ff)")  # Docker Methods
    DOCKER_GFN0_XTB = SimpleKeyword("docker(gfn0-xtb)")  # Docker Methods
    DOCKER_GFN1_XTB = SimpleKeyword("docker(gfn1-xtb)")  # Docker Methods
    DOCKER_GFN2_XTB = SimpleKeyword("docker(gfn2-xtb)")  # Docker Methods
    DOCKER_GFNFF = SimpleKeyword("docker(gfnff)")  # Docker Methods
    DOCKER_XTB = SimpleKeyword("docker(xtb)")  # Docker Methods
    DOCKER_XTB0 = SimpleKeyword("docker(xtb0)")  # Docker Methods
    DOCKER_XTB1 = SimpleKeyword("docker(xtb1)")  # Docker Methods
    QUICKDOCK = SimpleKeyword("quickdock")  # Docker Methods
    SCREENDOCK = SimpleKeyword("screendock")  # Docker Methods
