#!/usr/bin/env python3

import shutil
from pathlib import Path

from opi.core import Calculator
from opi.input.blocks import BlockIce
from opi.input.simple_keywords import BasisSet

if __name__ == "__main__":
    wd = Path("RUN")
    shutil.rmtree(wd, ignore_errors=True)
    wd.mkdir()

    calc = Calculator(basename="job", working_dir=wd)
    calc.input.add_simple_keywords(BasisSet.SV)

    calc.input.add_blocks(
        BlockIce(
            nel=10,
            norb=13,
            nroots=1,
            integrals="exact",
            icetype="CFGs",
            tgen=0.0001,
            tvar=0.00000000001,
            etol=0.000001,
        )
    )

    calc.write_input()
