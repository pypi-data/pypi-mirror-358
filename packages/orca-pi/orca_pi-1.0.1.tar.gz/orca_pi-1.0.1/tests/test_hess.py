from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["freq", "property", "hessian", "Hessian"]],
    indirect=True,
)
def test_hess(validate_json_schema):
    assert validate_json_schema
