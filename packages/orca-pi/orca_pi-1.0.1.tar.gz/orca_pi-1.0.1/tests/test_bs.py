from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["bs", "property", "broken_symmetry", "BrokenSym"]],
    indirect=True,
)
def test_bs(validate_json_schema):
    assert validate_json_schema
