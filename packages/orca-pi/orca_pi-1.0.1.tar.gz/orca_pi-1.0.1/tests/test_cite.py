from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "gbw", "citations", "Cite"],
        ["relative_corr", "gbw", "citations", "Cite"],
        ["opt", "gbw", "citations", "Cite"],
        ["uvvis", "gbw", "citations", "Cite"],
    ],
    indirect=True,
)
def test_cite(validate_json_schema):
    assert validate_json_schema
