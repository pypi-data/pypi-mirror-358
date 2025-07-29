from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["mp2", "property", "energy[1]", "Mp2Energy"]],
    indirect=True,
)
def test_mp2(validate_json_schema):
    assert validate_json_schema
