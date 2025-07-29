import pytest

from opi.output.grepper.recipes import (
    has_aborted_run,
    has_geometry_optimization_converged,
    has_scf_converged,
    has_terminated_normally,
)


@pytest.mark.parametrize("get_file", ["job.out"], indirect=True)
def test_terminated_normally(get_file):
    assert has_terminated_normally(get_file)


@pytest.mark.parametrize("get_file", ["abort.out"], indirect=True)
@pytest.mark.xfail
def test_not_terminated_normally(get_file):
    assert has_terminated_normally(get_file)


@pytest.mark.parametrize("get_file", ["abort.out"], indirect=True)
def test_aborted_termination(get_file):
    assert has_aborted_run(get_file)


@pytest.mark.parametrize("get_file", ["scf.out"], indirect=True)
@pytest.mark.xfail
def test_failed_aborted_termination(get_file):
    assert has_aborted_run(get_file)


@pytest.mark.parametrize("get_file", ["geometry.out"], indirect=True)
def test_has_geometry_optimization_converged(get_file):
    assert has_geometry_optimization_converged(get_file)


@pytest.mark.parametrize("get_file", ["failed_geometry.out"], indirect=True)
@pytest.mark.xfail
def test_failed_has_geometry_optimization_converged(get_file):
    assert has_geometry_optimization_converged(get_file)


@pytest.mark.parametrize("get_file", ["scf.out"], indirect=True)
def test_scf_converged(get_file):
    assert has_scf_converged(get_file)


@pytest.mark.parametrize("get_file", ["failed_scf.out"], indirect=True)
@pytest.mark.xfail
def test_failed_scf_converged(get_file):
    assert has_scf_converged(get_file)
