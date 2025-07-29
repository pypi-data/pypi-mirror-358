from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["epr", "property", "a_tensor", "Tensor"],
        ["cn_epr", "property", "a_tensor", "Tensor"],
    ],
    indirect=True,
)
def test_tensor(validate_json_schema):
    assert validate_json_schema
