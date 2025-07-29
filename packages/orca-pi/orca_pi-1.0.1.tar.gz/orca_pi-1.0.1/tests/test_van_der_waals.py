from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "property", "vdw_correction", "VdwCorrection"],
        ["opt", "property", "vdw_correction", "VdwCorrection"],
        ["dft", "property", "vdw_correction", "VdwCorrection"],
    ],
    indirect=True,
)
def test_vdw_correction(validate_json_schema):
    assert validate_json_schema
