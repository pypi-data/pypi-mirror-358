#!/usr/bin/env python3

import shutil
from pathlib import Path

from opi.core import Calculator
from opi.input.blocks import BlockScf
from opi.input.simple_keywords import BasisSet, Dft, Scf, ShellType
from opi.input.structures import Structure

if __name__ == "__main__":
    wd = Path("RUN")
    shutil.rmtree(wd, ignore_errors=True)
    wd.mkdir()

    calc = Calculator(basename="job", working_dir=wd)
    calc.structure = Structure.from_xyz("inp.xyz")
    calc.input.add_simple_keywords(ShellType.UKS, Dft.B3LYP_G, BasisSet.SVP, Scf.TIGHTSCF)

    calc.input.add_blocks(BlockScf(brokensym=[1, 1]))

    calc.write_input()
    calc.run()

    output = calc.get_output()
    if not output.terminated_normally():
        print(f"ORCA calculation failed, see output file: {output.get_outfile()}")
        exit(1)
    # << END OF IF

    # > Parse JSON files
    output.parse()
