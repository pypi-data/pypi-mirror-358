from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["nmr", "property", "spin_spin_coupling", "SpinSpinCoupling"]],
    indirect=True,
)
def test_spin_spin_coupling(validate_json_schema):
    assert validate_json_schema
