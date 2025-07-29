from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["roci", "property", "rocis_energies", "RoCiEnergy"]],
    indirect=True,
)
def test_roci_en(validate_json_schema):
    assert validate_json_schema
