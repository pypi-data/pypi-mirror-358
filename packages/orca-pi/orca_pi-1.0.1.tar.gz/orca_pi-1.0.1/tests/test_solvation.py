from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["cpcm", "property", "solvation_details", "SolvDetails"],
        ["uvvis", "property", "solvation_details", "SolvDetails"],
        ["nmr", "property", "solvation_details", "SolvDetails"],
        ["pop_analysis", "property", "solvation_details", "SolvDetails"],
    ],
    indirect=True,
)
def test_solv(validate_json_schema):
    assert validate_json_schema
