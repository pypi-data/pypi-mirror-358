from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["freq", "property", "dft_energy", "DftEnergy"],
        ["dft", "property", "dft_energy", "DftEnergy"],
        ["cpcm", "property", "dft_energy", "DftEnergy"],
        ["relative_corr", "property", "dft_energy", "DftEnergy"],
        ["rama", "property", "dft_energy", "DftEnergy"],
        ["uvvis", "property", "dft_energy", "DftEnergy"],
        ["epr", "property", "dft_energy", "DftEnergy"],
        ["bs", "property", "dft_energy", "DftEnergy"],
    ],
    indirect=True,
)
def test_dft_energy(validate_json_schema):
    assert validate_json_schema
