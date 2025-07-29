import pytest

from opi.output.grepper.core import Grepper
from opi.output.grepper.pre_condition import PreCondition


@pytest.mark.parametrize("get_file", ["scf.out"], indirect=True)
def test_grepper(get_file):
    """Searches for the Total SCF energy in EH"""
    test_grep = Grepper(get_file)
    test_pre_condition = [PreCondition("SCF ENERGY")]
    results = test_grep.search(
        "energy",
        pre_conditions=test_pre_condition,
        case_sensitive=False,
        matching_pattern=0,
        field=-4,
        field_sep=" ",
        trim_whitespaces=False,
        merge_sep=True,
        kind=float,
    )
    assert results == [-75.95933498564268]


@pytest.mark.parametrize("get_file", ["scf.out"], indirect=True)
def test_skip_line(get_file):
    """Searches for the Total SCF energy in EH"""
    test_grep = Grepper(get_file)
    results = test_grep.search(
        "SCF ENERGY",
        case_sensitive=False,
        matching_pattern=0,
        field=3,
        field_sep=" ",
        skip_lines=3,
        trim_whitespaces=False,
        merge_sep=True,
        kind=float,
    )
    assert results == [-75.95933498564268]


@pytest.mark.parametrize("get_file", ["scf.out"], indirect=True)
def test_field_sep(get_file):
    """Searches for all contributors named Dimitrios"""
    test_grep = Grepper(get_file)
    results = test_grep.search(
        "dimitrios",
        case_sensitive=False,
        field=0,
        field_sep=":",
        trim_whitespaces=True,
        merge_sep=True,
        kind=str,
    )
    assert results == ["Dimitrios Liakos", "Dimitrios Manganas", "Dimitrios Pantazis"]


@pytest.mark.parametrize("get_file", ["scf.out"], indirect=True)
def test_per_match(get_file):
    """Searches for the coordinates of the first oxygen atom"""
    test_grep = Grepper(get_file)

    test_pre_condition = [PreCondition("INPUT FILE", within=300, per_match=True)]

    results = test_grep.search(
        "O",
        pre_conditions=test_pre_condition,
        case_sensitive=True,
        matching_pattern=-1,
        field_sep=" ",
        kind=str,
        merge_sep=False,
    )
    assert results == ["| 14> O         -3.56626        1.77639        0.00000"]


@pytest.mark.parametrize("get_file", ["scf.out"], indirect=True)
def test_only_defaultvalues(get_file):
    """Searches for every doi mentioned in the output file"""
    test_grep = Grepper(get_file)
    results = test_grep.search("doi")
    assert results[1] == "doi.org/10.1002/wcms.1606"


@pytest.mark.parametrize("get_file", ["scf.out"], indirect=True)
def test_fallback(get_file):
    """Searches for a non existing string"""
    test_grep = Grepper(get_file)
    results = test_grep.search(
        "This string does not exist in the output file",
        case_sensitive=False,
        field=0,
        field_sep=":",
        trim_whitespaces=True,
        merge_sep=True,
        kind=str,
        fallback="string not found",
    )
    assert results == "string not found"


@pytest.mark.parametrize("get_file", ["scf.out"], indirect=True)
@pytest.mark.xfail
def test_match_parameter_out_of_bound(get_file):
    """Searches for the Total SCF but matching_pattern is out of bound"""
    """Searches for the Total SCF but matching_pattern is out of bound"""
    test_grep = Grepper(get_file)
    results = test_grep.search(
        "SCF ENERGY",
        case_sensitive=False,
        matching_pattern=100,
        field=3,
        field_sep=" ",
        skip_lines=3,
        trim_whitespaces=False,
        merge_sep=True,
        kind=float,
        fallback="This did not work, try to redfin parameters",
    )
    assert results == [-75.95933498564268]


@pytest.mark.parametrize("get_file", ["scf.out"], indirect=True)
@pytest.mark.xfail
def test_field_out_of_bound(get_file):
    """Searches for doi, with the field out o bound"""
    test_grep = Grepper(get_file)
    results = test_grep.search(
        "doi",
        case_sensitive=False,
        matching_pattern=1,
        field=300,
        field_sep=" ",
        trim_whitespaces=False,
        merge_sep=True,
        kind=float,
        fallback=["This did not work", "try to redfin parameters"],
    )
    assert results[1] == "doi.org/10.1002/wcms.1606"


@pytest.mark.parametrize("get_file", ["scf.out"], indirect=True)
@pytest.mark.xfail
def test_wrong_kind(get_file):
    """Searches for SCF energy, but expects an integer"""
    test_grep = Grepper(get_file)
    test_pre_condition = [PreCondition("SCF ENERGY")]
    results = test_grep.search(
        "energy",
        pre_conditions=test_pre_condition,
        case_sensitive=False,
        matching_pattern=0,
        field=-4,
        field_sep=" ",
        trim_whitespaces=False,
        merge_sep=True,
        kind=int,
    )
    assert results == [-75.95933498564268]
