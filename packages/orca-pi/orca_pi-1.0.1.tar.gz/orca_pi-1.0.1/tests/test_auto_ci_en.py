from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["autoci", "property", "energy[1]", "AutoCiEnergy"]],
    indirect=True,
)
def test_auto_ci(validate_json_schema):
    assert validate_json_schema
