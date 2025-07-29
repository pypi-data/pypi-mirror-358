from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["freq", "property", "thermochemistry_energies", "ThermochemistryEnergy"],
        ["rama", "property", "thermochemistry_energies", "ThermochemistryEnergy"],
    ],
    indirect=True,
)
def test_thermo(validate_json_schema):
    assert validate_json_schema
