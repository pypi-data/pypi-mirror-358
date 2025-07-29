#!/usr/bin/env python3

import shutil
from pathlib import Path

from opi.core import Calculator
from opi.input.blocks import BlockGeom
from opi.input.simple_keywords import BasisSet
from opi.input.simple_keywords import Method
from opi.input.simple_keywords import Scf
from opi.input.simple_keywords import Task
from opi.input.structures import Structure

if __name__ == "__main__":
    wd = Path("RUN")
    shutil.rmtree(wd, ignore_errors=True)
    wd.mkdir()

    # > constrained optimization
    calc_bond = Calculator(basename="job", working_dir=wd)
    calc_bond.structure = Structure.from_xyz("inp.xyz")
    calc_bond.input.add_simple_keywords(
        Scf.NOAUTOSTART,
        Method.HF,
        BasisSet.DEF2_SVP,
        Task.OPT,
    )

    constraints = ["B  0 1 1.5 C", "A  1 0 2 115.0 C", "D 6 1 0 2 60 C"]

    # > Constraint bonds, angles, dihedral
    calc_bond.input.add_blocks(BlockGeom(constraints=constraints))
    calc_bond.write_input()
    calc_bond.run()
