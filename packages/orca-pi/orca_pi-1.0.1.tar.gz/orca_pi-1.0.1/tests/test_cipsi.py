from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["cipsi", "property", "cipsi_energies", "CiPsi"]],
    indirect=True,
)
def test_cipsi(validate_json_schema):
    assert validate_json_schema
