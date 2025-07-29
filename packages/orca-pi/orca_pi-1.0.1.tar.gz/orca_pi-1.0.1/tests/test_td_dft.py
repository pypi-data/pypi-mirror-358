from pytest import mark


@mark.parametrize("validate_json_schema", [["uvvis", "gbw", "td-dft", "TdDft"]], indirect=True)
def test_td_dft(validate_json_schema):
    assert validate_json_schema
