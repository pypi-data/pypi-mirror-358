from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Scf",)


class Scf(SimpleKeywordBox):
    """Enum to store all simple keywords of type Scf"""

    G3CONV = SimpleKeyword("3conv")  # SCF solver combination
    AODIISTRAH = SimpleKeyword("aodiistrah")  # SCF solver combination
    DIISTRAH = SimpleKeyword("diistrah")  # SCF solver combination
    KDIISTRAH = SimpleKeyword("kdiistrah")  # SCF solver combination
    DIIS = SimpleKeyword("diis")  # SCF solver
    NODIIS = SimpleKeyword("nodiis")  # SCF solver
    AODIIS = SimpleKeyword("aodiis")  # SCF solver
    NOAODIIS = SimpleKeyword("noaodiis")  # SCF solver
    KDIIS = SimpleKeyword("kdiis")  # SCF solver
    NOKDIIS = SimpleKeyword("nokdiis")  # SCF solver
    SOSCF = SimpleKeyword("soscf")  # SCF solver
    NOSOSCF = SimpleKeyword("nososcf")  # SCF solver
    TRAH = SimpleKeyword("trah")  # SCF solver
    NOTRAH = SimpleKeyword("notrah")  # SCF solver
    AUTOSTART = SimpleKeyword(
        "autostart"
    )  # SCF initial guess start SCF from a gbw file with the same basename (default)
    NOAUTOSTART = SimpleKeyword(
        "noautostart"
    )  # SCF initial guess do not start SCF from a gbw file with the same basename
    MOREAD = SimpleKeyword("moread")  # SCF initial guess read orbitals from gbw file
    EHTANO = SimpleKeyword("ehtano")  # SCF initial guess
    HCORE = SimpleKeyword("hcore")  # SCF initial guess
    HUECKEL = SimpleKeyword("hueckel")  # SCF initial guess
    PATOM = SimpleKeyword("patom")  # SCF initial guess
    PMODEL = SimpleKeyword("pmodel")  # SCF initial guess
    PMODELX = SimpleKeyword("pmodelx")  # SCF initial guess
    PMODELXAV = SimpleKeyword("pmodelxav")  # SCF initial guess
    PMODELXPM = SimpleKeyword("pmodelxpm")  # SCF initial guess
    SYMBREAKGUESS = SimpleKeyword("symbreakguess")  # SCF initial guess
    UNITMATRIXGUESS = SimpleKeyword("unitmatrixguess")  # SCF initial guess
    USEGRAMSCHMIDT = SimpleKeyword("usegramschmidt")  # SCF initial guess
    CALCGUESSENERGY = SimpleKeyword("calcguessenergy")  # Calculate the guess energy
    CONV = SimpleKeyword("conv")  # Conventional SCF
    SEMIDIRECT = SimpleKeyword("semidirect")  # Semidirect SCF
    DIRECT = SimpleKeyword("direct")  # Direct SCF
    SCFSTAB = SimpleKeyword("scfstab")  # SCF stability analysis
    NOSCFSTAB = SimpleKeyword("noscfstab")  # No SCF stability analysis
    DELTASCF = SimpleKeyword("deltascf")  # DeltaSCF for access to excited states
    FRSOSCF = SimpleKeyword("frsoscf")  # freeze and release DeltaSCF settings
    GMF = SimpleKeyword("gmf")  # DeltaSCF settings
    SMEAR = SimpleKeyword("smear")  # do finite temperature DFT (smearing)
    NOSMEAR = SimpleKeyword("nosmear")  # do not use finite temperature DFT (smearing)
    FRACOCC = SimpleKeyword("fracocc")  # enable fractional occupations
    SCFCONVFORCED = SimpleKeyword(
        "scfconvforced"
    )  # Force SCF convergence for subsequent operations
    SLOPPYSCF = SimpleKeyword("sloppyscf")  # SCF convergence threshold settings
    LOOSESCF = SimpleKeyword("loosescf")  # SCF convergence threshold settings
    NORMALSCF = SimpleKeyword("normalscf")  # SCF convergence threshold settings
    STRONGSCF = SimpleKeyword("strongscf")  # SCF convergence threshold settings
    TIGHTSCF = SimpleKeyword("tightscf")  # SCF convergence threshold settings
    VERYTIGHTSCF = SimpleKeyword("verytightscf")  # SCF convergence threshold settings
    EXTREMESCF = SimpleKeyword("extremescf")  # SCF convergence threshold settings
    SLOPPYSCFCHECK = SimpleKeyword("sloppyscfcheck")  # SCF convergence threshold settings
    NOSLOPPYSCFCHECK = SimpleKeyword("nosloppyscfcheck")  # SCF convergence threshold settings
    SCFCHECKGRAD = SimpleKeyword("scfcheckgrad")  # SCF convergence threshold settings
    SCFCONV6 = SimpleKeyword("scfconv6")  # SCF convergence threshold settings
    SCFCONV7 = SimpleKeyword("scfconv7")  # SCF convergence threshold settings
    SCFCONV8 = SimpleKeyword("scfconv8")  # SCF convergence threshold settings
    SCFCONV9 = SimpleKeyword("scfconv9")  # SCF convergence threshold settings
    SCFCONV10 = SimpleKeyword("scfconv10")  # SCF convergence threshold settings
    SCFCONV11 = SimpleKeyword("scfconv11")  # SCF convergence threshold settings
    SCFCONV12 = SimpleKeyword("scfconv12")  # SCF convergence threshold settings
    EASYCONV = SimpleKeyword("easyconv")  # SCF convergence strategy
    NORMALCONV = SimpleKeyword("normalconv")  # SCF convergence strategy
    SLOWCONV = SimpleKeyword("slowconv")  # SCF convergence strategy
    VERYSLOWCONV = SimpleKeyword("veryslowconv")  # SCF convergence strategy
    DAMP = SimpleKeyword("damp")  # SCF settings
    NODAMP = SimpleKeyword("nodamp")  # SCF settings
    LSHIFT = SimpleKeyword("lshift")  # SCF settings
    NOLSHIFT = SimpleKeyword("nolshift")  # SCF settings
    USEINCREMENTAL = SimpleKeyword("useincremental")  # SCF settings
    NOINCREMENTAL = SimpleKeyword("noincremental")  # SCF settings
    NOITER = SimpleKeyword("noiter")  # SCF settings no iterations
    SCFLBFGS = SimpleKeyword("scflbfgs")  # SOSCF settings
    SCFLBOFILL = SimpleKeyword("scflbofill")  # SOSCF settings
    SCFLPOWELL = SimpleKeyword("scflpowell")  # SOSCF settings
    SCFLSR1 = SimpleKeyword("scflsr1")  # SOSCF settings
    NOTRAHRANDOMIZE = SimpleKeyword("notrahrandomize")  # TRAH settings
