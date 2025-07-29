#!/usr/bin/env python3

import shutil
from pathlib import Path

from opi.core import Calculator
from opi.input.simple_keywords import BasisSet, Dft, Scf, Task
from opi.input.structures import Structure

if __name__ == "__main__":
    wd = Path("RUN")
    shutil.rmtree(wd, ignore_errors=True)
    wd.mkdir()

    calc = Calculator(basename="job", working_dir=wd)
    calc.structure = Structure.from_xyz("inp.xyz")
    calc.input.add_simple_keywords(Scf.NOAUTOSTART, Dft.WB97X3C, BasisSet.DEF2_TZVP, Task.OPT)
    calc.input.ncores = 4

    calc.write_input()
    calc.run()

    output = calc.get_output()
    if not output.terminated_normally():
        print(f"ORCA calculation failed, see output file: {output.get_outfile()}")
        exit(1)
    # << END OF IF

    # > Parse JSON files
    output.parse()

    ngeoms = len(output.results_properties.geometries)
    print("N GEOMETRIES")
    print(ngeoms)
    print("FINAL SINGLE POINT ENERGY")
    print(output.results_properties.geometries[-1].single_point_data.finalenergy)
    print("SCF Energy along trajectory")
    # > Geometry index starts from 1 to *ngeom*
    for igeom in range(0, ngeoms):
        print(
            f"{igeom})", output.results_properties.geometries[igeom].single_point_data.finalenergy
        )
    print("Mulliken charges along trajectory")
    # > Geometry index starts from 1 to *ngeom*
    for igeom in range(0, ngeoms):
        try:
            charges = (
                output.results_properties.geometries[igeom]
                .mulliken_population_analysis[0]
                .atomiccharges
            )
        except TypeError:
            charges = "n/a"
        print(f"{igeom})", charges)
