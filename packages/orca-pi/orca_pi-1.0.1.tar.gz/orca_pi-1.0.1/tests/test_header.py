from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "gbw", "orca header", "OrcaHeader"],
        ["relative_corr", "gbw", "orca header", "OrcaHeader"],
        ["opt", "gbw", "orca header", "OrcaHeader"],
        ["uvvis", "gbw", "orca header", "OrcaHeader"],
    ],
    indirect=True,
)
def test_header(validate_json_schema):
    assert validate_json_schema
