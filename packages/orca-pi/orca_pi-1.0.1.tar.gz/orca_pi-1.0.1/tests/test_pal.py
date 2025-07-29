from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["pal", "property", "pal_flags", "PalFlags"]],
    indirect=True,
)
@mark.skip(reason="JSON property file does not include this information at the moment.")
def test_pal(validate_json_schema):
    assert validate_json_schema
