from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["cn_epr", "property", "efg_tensor", "EfgTensor"]],
    indirect=True,
)
def test_efg_tensor(validate_json_schema):
    assert validate_json_schema
