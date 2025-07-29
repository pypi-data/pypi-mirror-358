from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Task",)


class Task(SimpleKeywordBox):
    """Enum to store all simple keywords of type Task"""

    SP = SimpleKeyword("sp")  # perform a single point energy calculation (default)
    ENGRAD = SimpleKeyword("engrad")  # Energy and gradient
    OPT = SimpleKeyword("opt")  # Perform geometry optimization
    FREQ = SimpleKeyword("freq")  # analytical frequency calculation
    NUMFREQ = SimpleKeyword("numfreq")  # numerical frequency calculation
    MD = SimpleKeyword("md")  # molecular dynamics
    EDA = SimpleKeyword("eda")  # Perform an eda analysis
    AUTOFRAG = SimpleKeyword("autofrag")  # Automatic detection of fragments
    CIM = SimpleKeyword("cim")  # Calculate energy with clusters in molecule approach
    CRUDEOPT = SimpleKeyword("crudeopt")  # Geometry optimization with thresholds
    LOOSEOPT = SimpleKeyword("looseopt")  # Geometry optimization with thresholds
    NORMALOPT = SimpleKeyword("normalopt")  # Geometry optimization with thresholds
    SLOPPYOPT = SimpleKeyword("sloppyopt")  # Geometry optimization with thresholds
    TIGHTOPT = SimpleKeyword("tightopt")  # Geometry optimization with thresholds
    VERYTIGHTOPT = SimpleKeyword("verytightopt")  # Geometry optimization with thresholds
    OPTH = SimpleKeyword("opth")  # Optimize only hydrogen atoms
    COPT = SimpleKeyword("copt")  # Perform geometry optimization (cartesian coordinates)
    L_OPT = SimpleKeyword("l-opt")  # Perform geometry optimization with lopt
    L_OPTH = SimpleKeyword("l-opth")  # Optimize only hydrogen atoms
    EXTOPT = SimpleKeyword(
        "extopt"
    )  # Use only the geometry optimizer from orca with external energy/gradient
    OPTTS = SimpleKeyword("optts")  # optimize transition state
    OPTTS_GMF = SimpleKeyword("optts(gmf)")  # optimize transition state
    QMMMOPT = SimpleKeyword("qmmmopt")  # Optimize the geometry with qmmm
    QMMMOPT_PDYNAMO = SimpleKeyword("qmmmopt/pdynamo")  # Optimize the geometry with qmmm
    RIGIDBODYOPT = SimpleKeyword("rigidbodyopt")  # Optimize fragments as rigid bodies
    CI_OPT = SimpleKeyword("ci-opt")  # conical-intersection optimization
    MECP_OPT = SimpleKeyword("mecp-opt")  # MECP optimization
    NEB = SimpleKeyword("neb")  # NEB for finding minimal energy pathways (and transition states)
    NEB_CI = SimpleKeyword(
        "neb-ci"
    )  # NEB for finding minimal energy pathways (and transition states)
    NEB_IDPP = SimpleKeyword(
        "neb-idpp"
    )  # NEB for finding minimal energy pathways (and transition states)
    NEB_MMFTS = SimpleKeyword(
        "neb-mmfts"
    )  # NEB for finding minimal energy pathways (and transition states)
    NEB_TS = SimpleKeyword(
        "neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    FAST_NEB_TS = SimpleKeyword(
        "fast-neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    LOOSE_NEB_TS = SimpleKeyword(
        "loose-neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    TIGHT_NEB_TS = SimpleKeyword(
        "tight-neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    ZOOM_NEB = SimpleKeyword(
        "zoom-neb"
    )  # NEB for finding minimal energy pathways (and transition states)
    ZOOM_NEB_CI = SimpleKeyword(
        "zoom-neb-ci"
    )  # NEB for finding minimal energy pathways (and transition states)
    ZOOM_NEB_TS = SimpleKeyword(
        "zoom-neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    FLAT_NEB_TS = SimpleKeyword(
        "flat-neb-ts"
    )  # NEB for finding minimal energy pathways (and transition states)
    IRC = SimpleKeyword("irc")  # internal reaction coordinate
    SCANTS = SimpleKeyword("scants")  # scan for transition state
    GOAT = SimpleKeyword("goat")  # GOAT Methods
    GOAT_COARSE = SimpleKeyword("goat-coarse")  # GOAT Methods
    GOAT_DIVERSITY = SimpleKeyword("goat-diversity")  # GOAT Methods
    GOAT_ENTROPY = SimpleKeyword("goat-entropy")  # GOAT Methods
    GOAT_EXPLORE = SimpleKeyword("goat-explore")  # GOAT Methods
    GOAT_REACT = SimpleKeyword("goat-react")  # GOAT Methods
    GOAT_TS = SimpleKeyword("goat-ts")  # GOAT Methods
    NORMALDOCK = SimpleKeyword("normaldock")  # Docker Methods
    COMPLETEDOCK = SimpleKeyword("completedock")  # Docker Methods
    DOCK_GFN_FF = SimpleKeyword("dock(gfn-ff)")  # Docker Methods
    DOCK_GFN0_XTB = SimpleKeyword("dock(gfn0-xtb)")  # Docker Methods
    DOCK_GFN1_XTB = SimpleKeyword("dock(gfn1-xtb)")  # Docker Methods
    DOCK_GFN2_XTB = SimpleKeyword("dock(gfn2-xtb)")  # Docker Methods
    DOCK_GFNFF = SimpleKeyword("dock(gfnff)")  # Docker Methods
    DOCK_XTB = SimpleKeyword("dock(xtb)")  # Docker Methods
    DOCK_XTB0 = SimpleKeyword("dock(xtb0)")  # Docker Methods
    DOCK_XTB1 = SimpleKeyword("dock(xtb1)")  # Docker Methods
    DOCKER = SimpleKeyword("docker")  # Docker Methods
    DOCKER_GFN_FF = SimpleKeyword("docker(gfn-ff)")  # Docker Methods
    DOCKER_GFN0_XTB = SimpleKeyword("docker(gfn0-xtb)")  # Docker Methods
    DOCKER_GFN1_XTB = SimpleKeyword("docker(gfn1-xtb)")  # Docker Methods
    DOCKER_GFN2_XTB = SimpleKeyword("docker(gfn2-xtb)")  # Docker Methods
    DOCKER_GFNFF = SimpleKeyword("docker(gfnff)")  # Docker Methods
    DOCKER_XTB = SimpleKeyword("docker(xtb)")  # Docker Methods
    DOCKER_XTB0 = SimpleKeyword("docker(xtb0)")  # Docker Methods
    DOCKER_XTB1 = SimpleKeyword("docker(xtb1)")  # Docker Methods
    QUICKDOCK = SimpleKeyword("quickdock")  # Docker Methods
    SCREENDOCK = SimpleKeyword("screendock")  # Docker Methods
    SOLVATOR = SimpleKeyword("solvator")  # Use the solvator for explicit solvation
    ENMGRAD = SimpleKeyword("enmgrad")  # Energy normal mode gradient
    CALCESTHESS = SimpleKeyword("calcesthess")  # Calculate an approximate hessian
    MT = SimpleKeyword("mt")  # mode trajectory
    NMSCAN = SimpleKeyword("nmscan")  # normal mode scan
    PRINTTHERMOCHEM = SimpleKeyword("printthermochem")  # Only do thermostatistical corrections
    PROPERTIESONLY = SimpleKeyword("propertiesonly")  # Only calc properties
    NUMNAC = SimpleKeyword("numnac")  # Numerical non-adiabatic coupling
