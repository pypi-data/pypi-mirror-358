from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "property", "coordinates", "Coordinates"],
        ["ccsdt", "property", "coordinates", "Coordinates"],
        ["opt", "property", "coordinates", "Coordinates"],
        ["freq", "property", "coordinates", "Coordinates"],
        ["dft", "property", "coordinates", "Coordinates"],
        ["mp2", "property", "coordinates", "Coordinates"],
        ["cpcm", "property", "coordinates", "Coordinates"],
        ["relative_corr", "property", "coordinates", "Coordinates"],
        ["rama", "property", "coordinates", "Coordinates"],
        ["uvvis", "property", "coordinates", "Coordinates"],
        ["epr", "property", "coordinates", "Coordinates"],
        ["nmr", "property", "coordinates", "Coordinates"],
        ["bs", "property", "coordinates", "Coordinates"],
        ["led", "property", "coordinates", "Coordinates"],
        ["pop_analysis", "property", "coordinates", "Coordinates"],
        ["autoci", "property", "coordinates", "Coordinates"],
        ["roci", "property", "coordinates", "Coordinates"],
        ["energy_extrap", "property", "coordinates", "Coordinates"],
        ["cipsi", "property", "coordinates", "Coordinates"],
        ["casscf", "property", "coordinates", "Coordinates"],
        ["cn_epr", "property", "coordinates", "Coordinates"],
        ["mbis", "property", "coordinates", "Coordinates"],
        ["pal", "property", "coordinates", "Coordinates"],
    ],
    indirect=True,
)
def test_coord(validate_json_schema):
    assert validate_json_schema
