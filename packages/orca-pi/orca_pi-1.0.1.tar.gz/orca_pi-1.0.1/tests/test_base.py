from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "gbw", "basis", "Base"],
        ["relative_corr", "gbw", "basis", "Base"],
        ["opt", "gbw", "basis", "Base"],
        ["uvvis", "gbw", "basis", "Base"],
    ],
    indirect=True,
)
def test_base(validate_json_schema):
    assert validate_json_schema
