from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "gbw", "mos", "MO"],
        ["relative_corr", "gbw", "mos", "MO"],
        ["opt", "gbw", "mos", "MO"],
        ["uvvis", "gbw", "mos", "MO"],
    ],
    indirect=True,
)
def test_mos(validate_json_schema):
    assert validate_json_schema
