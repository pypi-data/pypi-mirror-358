from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["opt", "property", "nuclear_gradient", "NucGradient"],
        ["relative_corr", "property", "nuclear_gradient", "NucGradient"],
    ],
    indirect=True,
)
def test_gradient(validate_json_schema):
    assert validate_json_schema
