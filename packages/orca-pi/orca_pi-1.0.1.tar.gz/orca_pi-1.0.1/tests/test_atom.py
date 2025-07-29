from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "gbw", "atoms", "Atoms"],
        ["relative_corr", "gbw", "atoms", "Atoms"],
        ["opt", "gbw", "atoms", "Atoms"],
        ["uvvis", "gbw", "atoms", "Atoms"],
    ],
    indirect=True,
)
def test_atom(validate_json_schema):
    assert validate_json_schema
