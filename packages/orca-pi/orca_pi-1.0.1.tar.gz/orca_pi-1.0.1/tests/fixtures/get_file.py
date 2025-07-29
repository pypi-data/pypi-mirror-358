from pathlib import Path

import pytest
from pytest import FixtureRequest


@pytest.fixture
def get_file(request: FixtureRequest) -> Path:
    """
    Returns the path to the output file for test

    Parameters
    ----------
    request: FixtureRequest

    Returns
    -------
    Path
        Path to the output

    """
    return Path(__file__).resolve().parent / "output_files" / request.param
