from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "property", "dipole_moment", "Dipole"],
        ["ccsdt", "property", "dipole_moment", "Dipole"],
        ["opt", "property", "dipole_moment", "Dipole"],
        ["freq", "property", "dipole_moment", "Dipole"],
        ["dft", "property", "dipole_moment", "Dipole"],
        ["mp2", "property", "dipole_moment", "Dipole"],
        ["cpcm", "property", "dipole_moment", "Dipole"],
        ["relative_corr", "property", "dipole_moment", "Dipole"],
        ["rama", "property", "dipole_moment", "Dipole"],
        ["uvvis", "property", "dipole_moment", "Dipole"],
        ["epr", "property", "dipole_moment", "Dipole"],
        ["nmr", "property", "dipole_moment", "Dipole"],
        ["bs", "property", "dipole_moment", "Dipole"],
        ["led", "property", "dipole_moment", "Dipole"],
        ["pop_analysis", "property", "dipole_moment", "Dipole"],
        ["autoci", "property", "dipole_moment", "Dipole"],
        ["roci", "property", "dipole_moment", "Dipole"],
        ["energy_extrap", "property", "dipole_moment", "Dipole"],
        ["cipsi", "property", "dipole_moment", "Dipole"],
        ["casscf", "property", "dipole_moment", "Dipole"],
        ["cn_epr", "property", "dipole_moment", "Dipole"],
        ["mbis", "property", "dipole_moment", "Dipole"],
        ["pal", "property", "dipole_moment", "Dipole"],
    ],
    indirect=True,
)
def test_dipole_moment(validate_json_schema):
    assert validate_json_schema
