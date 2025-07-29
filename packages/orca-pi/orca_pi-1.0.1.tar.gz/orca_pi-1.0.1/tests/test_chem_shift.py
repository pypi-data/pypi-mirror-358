from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["nmr", "property", "chemical_shift", "ChemicalShift"]],
    indirect=True,
)
def test_chem_shift(validate_json_schema):
    assert validate_json_schema
