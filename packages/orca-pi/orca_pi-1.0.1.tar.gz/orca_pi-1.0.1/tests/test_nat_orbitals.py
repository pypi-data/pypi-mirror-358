from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["bs", "property", "natural_orbitals", "NaturalOrbitals"]],
    indirect=True,
)
def test_nat_orbitals(validate_json_schema):
    assert validate_json_schema
