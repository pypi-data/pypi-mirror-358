from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["energy_extrap", "property", "energy_extrapolation", "EnergyExtrapolation"]],
    indirect=True,
)
def test_efg_tensor(validate_json_schema):
    assert validate_json_schema
