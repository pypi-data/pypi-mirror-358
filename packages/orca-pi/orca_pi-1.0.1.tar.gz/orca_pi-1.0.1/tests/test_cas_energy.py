from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["casscf", "property", "energy[0]", "CasEnergy"]],
    indirect=True,
)
def test_casscf(validate_json_schema):
    assert validate_json_schema
