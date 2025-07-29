from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "property", "geometry", "Geometry"],
        ["ccsdt", "property", "geometry", "Geometry"],
        ["opt", "property", "geometry", "Geometry"],
        ["freq", "property", "geometry", "Geometry"],
        ["dft", "property", "geometry", "Geometry"],
        ["mp2", "property", "geometry", "Geometry"],
        ["cpcm", "property", "geometry", "Geometry"],
        ["relative_corr", "property", "geometry", "Geometry"],
        ["rama", "property", "geometry", "Geometry"],
        ["uvvis", "property", "geometry", "Geometry"],
        ["epr", "property", "geometry", "Geometry"],
        ["nmr", "property", "geometry", "Geometry"],
        ["bs", "property", "geometry", "Geometry"],
        ["led", "property", "geometry", "Geometry"],
        ["pop_analysis", "property", "geometry", "Geometry"],
        ["autoci", "property", "geometry", "Geometry"],
        ["roci", "property", "geometry", "Geometry"],
        ["energy_extrap", "property", "geometry", "Geometry"],
        ["cipsi", "property", "geometry", "Geometry"],
        ["casscf", "property", "geometry", "Geometry"],
        ["cn_epr", "property", "geometry", "Geometry"],
        ["mbis", "property", "geometry", "Geometry"],
        ["pal", "property", "geometry", "Geometry"],
    ],
    indirect=True,
)
def test_geometry(validate_json_schema):
    assert validate_json_schema
