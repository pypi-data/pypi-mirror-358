from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "gbw", "molecularorbitals", "MolecularOrbitals"],
        ["relative_corr", "gbw", "molecularorbitals", "MolecularOrbitals"],
        ["opt", "gbw", "molecularorbitals", "MolecularOrbitals"],
        ["uvvis", "gbw", "molecularorbitals", "MolecularOrbitals"],
    ],
    indirect=True,
)
def test_molecular_orbitals(validate_json_schema):
    assert validate_json_schema
