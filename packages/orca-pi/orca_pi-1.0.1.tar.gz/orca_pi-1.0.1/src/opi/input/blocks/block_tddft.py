from opi.input.blocks.block_cis import BlockCis

__all__ = ("BlockTddft",)


class BlockTddft(BlockCis):
    """
    Class to model %tddft block in ORCA.
    Since it is the same as the %cis block, it is defined here as a derived class of BlockCis.
    """

    _name = "tddft"
