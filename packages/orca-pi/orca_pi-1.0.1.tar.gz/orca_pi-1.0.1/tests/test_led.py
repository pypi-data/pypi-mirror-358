from pytest import mark


@mark.parametrize("validate_json_schema", [["led", "property", "mdci_led", "Led"]], indirect=True)
def test_led(validate_json_schema):
    assert validate_json_schema
