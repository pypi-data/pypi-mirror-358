from pytest import mark


@mark.parametrize(
    "validate_json_schema",
    [
        ["scf", "property", "energy[0]", "ScfEnergy"],
        ["ccsdt", "property", "energy[0]", "ScfEnergy"],
        ["opt", "property", "energy[0]", "ScfEnergy"],
        ["freq", "property", "energy[0]", "ScfEnergy"],
        ["dft", "property", "energy[0]", "ScfEnergy"],
        ["mp2", "property", "energy[0]", "ScfEnergy"],
        ["cpcm", "property", "energy[0]", "ScfEnergy"],
        ["relative_corr", "property", "energy[0]", "ScfEnergy"],
        ["rama", "property", "energy[0]", "ScfEnergy"],
        ["uvvis", "property", "energy[0]", "ScfEnergy"],
        ["epr", "property", "energy[0]", "ScfEnergy"],
        ["nmr", "property", "energy[0]", "ScfEnergy"],
        ["bs", "property", "energy[0]", "ScfEnergy"],
        ["led", "property", "energy[0]", "ScfEnergy"],
        ["pop_analysis", "property", "energy[0]", "ScfEnergy"],
        ["autoci", "property", "energy[0]", "ScfEnergy"],
        ["roci", "property", "energy[0]", "ScfEnergy"],
        ["energy_extrap", "property", "energy[0]", "ScfEnergy"],
        ["cipsi", "property", "energy[0]", "ScfEnergy"],
        ["cn_epr", "property", "energy[0]", "ScfEnergy"],
        ["mbis", "property", "energy[0]", "ScfEnergy"],
        ["pal", "property", "energy[0]", "ScfEnergy"],
    ],
    indirect=True,
)
def test_scf_energy(validate_json_schema):
    assert validate_json_schema
