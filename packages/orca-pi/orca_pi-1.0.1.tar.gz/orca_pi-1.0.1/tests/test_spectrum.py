from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["uvvis", "property", "absorption_spectrum", "Spectrum"],
        ["roci", "property", "absorption_spectrum", "Spectrum"],
    ],
    indirect=True,
)
def test_absorption(validate_json_schema):
    assert validate_json_schema


@mark.parametrize(
    "validate_json_schema",
    [
        ["uvvis", "property", "ecd_spectrum", "Spectrum"],
        ["roci", "property", "ecd_spectrum", "Spectrum"],
    ],
    indirect=True,
)
def test_ecd_spectrum(validate_json_schema):
    assert validate_json_schema
