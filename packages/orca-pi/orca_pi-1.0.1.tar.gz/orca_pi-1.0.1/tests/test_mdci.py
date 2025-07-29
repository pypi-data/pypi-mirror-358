from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["ccsdt", "property", "energy[1]", "Mdcisd_t_Energies"],
        ["led", "property", "energy[1]", "Mdcisd_t_Energies"],
    ],
    indirect=True,
)
def test_mdci(validate_json_schema):
    assert validate_json_schema
