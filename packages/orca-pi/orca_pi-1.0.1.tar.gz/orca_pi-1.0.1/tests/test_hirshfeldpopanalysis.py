from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        [
            "pop_analysis",
            "property",
            "hirshfeld_population_analysis",
            "HirshfeldPopulationAnalysis",
        ]
    ],
    indirect=True,
)
def test_hirschfeld_population_analysis(validate_json_schema):
    assert validate_json_schema
