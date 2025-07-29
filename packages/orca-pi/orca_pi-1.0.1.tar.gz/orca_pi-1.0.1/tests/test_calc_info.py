from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "property", "calculation_info", "CalcInfo"],
        ["ccsdt", "property", "calculation_info", "CalcInfo"],
        ["freq", "property", "calculation_info", "CalcInfo"],
        ["dft", "property", "calculation_info", "CalcInfo"],
        ["mp2", "property", "calculation_info", "CalcInfo"],
        ["cpcm", "property", "calculation_info", "CalcInfo"],
        ["uvvis", "property", "calculation_info", "CalcInfo"],
        ["epr", "property", "calculation_info", "CalcInfo"],
        ["nmr", "property", "calculation_info", "CalcInfo"],
        ["bs", "property", "calculation_info", "CalcInfo"],
        ["led", "property", "calculation_info", "CalcInfo"],
        ["pop_analysis", "property", "calculation_info", "CalcInfo"],
        ["autoci", "property", "calculation_info", "CalcInfo"],
        ["roci", "property", "calculation_info", "CalcInfo"],
        ["energy_extrap", "property", "calculation_info", "CalcInfo"],
        ["cipsi", "property", "calculation_info", "CalcInfo"],
        ["casscf", "property", "calculation_info", "CalcInfo"],
        ["cn_epr", "property", "calculation_info", "CalcInfo"],
        ["mbis", "property", "calculation_info", "CalcInfo"],
    ],
    indirect=True,
)
def test_calc_info(validate_json_schema):
    assert validate_json_schema
