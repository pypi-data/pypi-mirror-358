from pytest import mark


@mark.parametrize(
    "validate_json_schema", [["epr", "property", "g_tensor", "Gtensor"]], indirect=True
)
def test_efg_tensor(validate_json_schema):
    assert validate_json_schema
