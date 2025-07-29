from opi.input.blocks.base import Block

__all__ = ("BlockMethod",)


class BlockMethod(Block):
    """Class to model %method block in ORCA"""

    _name: str = "Method"

    # > Options
    d3s6: float | None = None
    d3a1: float | None = None
    d3s8: float | None = None
    d3a2: float | None = None
