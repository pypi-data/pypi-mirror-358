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

    # > Scan a bond length with a relaxed surface scan
    calc_bond = Calculator(basename="scan_bond", working_dir=wd)
    calc_bond.structure = Structure.from_xyz("inp.xyz")
    calc_bond.input.add_simple_keywords(
        Scf.NOAUTOSTART,
        Method.HF,
        BasisSet.DEF2_SVP,
        Task.OPT,
    )

    calc_bond.input.add_blocks(BlockGeom(scan="B  0  1 = 1.1, 2.1, 5"))
    calc_bond.write_input()
    calc_bond.run()

    # > Scan an angle with a relaxed surface scan
    calc_angle = Calculator(basename="scan_angle", working_dir=wd)
    calc_angle.structure = Structure.from_xyz("inp.xyz")
    calc_angle.input.add_simple_keywords(
        Scf.NOAUTOSTART,
        Method.HF,
        BasisSet.DEF2_SVP,
        Task.OPT,
    )

    calc_angle.input.add_blocks(BlockGeom(scan="A  1 0 2 = 110, 170, 6"))
    calc_angle.write_input()
    calc_angle.run()

    # > Scan a dihedral with a relaxed surface scan
    calc_dihedral = Calculator(basename="scan_dihedral", working_dir=wd)
    calc_dihedral.structure = Structure.from_xyz("inp.xyz")
    calc_dihedral.input.add_simple_keywords(
        Scf.NOAUTOSTART,
        Method.HF,
        BasisSet.DEF2_SVP,
        Task.OPT,
    )

    calc_dihedral.input.add_blocks(BlockGeom(scan="D 6 1 0 2 = 60, 120, 6"))
    calc_dihedral.write_input()
    calc_dihedral.run()
