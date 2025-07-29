from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["pop_analysis", "property", "quadrupole_moment", "QuadrupoleMoment"]],
    indirect=True,
)
def test_quadruple_moment(validate_json_schema):
    assert validate_json_schema
