from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["rama", "property", "polarizability", "Polarizability"],
        ["pop_analysis", "property", "polarizability", "Polarizability"],
    ],
    indirect=True,
)
def test_nat_orbitals(validate_json_schema):
    assert validate_json_schema
