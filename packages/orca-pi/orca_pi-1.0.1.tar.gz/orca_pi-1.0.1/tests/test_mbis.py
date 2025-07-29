from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [["mbis", "property", "mbis_population_analysis", "MbisPopAnalysis"]],
    indirect=True,
)
def test_mbispopanalysis(validate_json_schema):
    assert validate_json_schema
