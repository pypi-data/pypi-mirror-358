from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["rama", "property", "loewdin_population_analysis", "PopulationAnalysis"],
        ["cipsi", "property", "loewdin_population_analysis", "PopulationAnalysis"],
    ],
    indirect=True,
)
def test_loewedin_populationanalysis(validate_json_schema):
    assert validate_json_schema


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["ccsdt", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["opt", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["freq", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["dft", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["mp2", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["cpcm", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        [
            "relative_corr",
            "property",
            "mulliken_population_analysis",
            "PopulationAnalysis",
        ],
        ["rama", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["uvvis", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["epr", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["nmr", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["bs", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["led", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        [
            "pop_analysis",
            "property",
            "mulliken_population_analysis",
            "PopulationAnalysis",
        ],
        ["autoci", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["cn_epr", "property", "mulliken_population_analysis", "PopulationAnalysis"],
        ["mbis", "property", "mulliken_population_analysis", "PopulationAnalysis"],
    ],
    indirect=True,
)
def test_mulliken_population_analysis(validate_json_schema):
    assert validate_json_schema
