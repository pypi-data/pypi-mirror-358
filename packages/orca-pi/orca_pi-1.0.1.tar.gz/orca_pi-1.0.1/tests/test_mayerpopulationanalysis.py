from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        [
            "pop_analysis",
            "property",
            "mayer_population_analysis",
            "MayerPopulationAnalysis",
        ]
    ],
    indirect=True,
)
def test_mayerpopanalysis(validate_json_schema):
    assert validate_json_schema
