from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "gbw", "molecule", "Molecule"],
        ["relative_corr", "gbw", "molecule", "Molecule"],
        ["opt", "gbw", "molecule", "Molecule"],
        ["uvvis", "gbw", "molecule", "Molecule"],
    ],
    indirect=True,
)
def test_molecule(validate_json_schema):
    assert validate_json_schema
