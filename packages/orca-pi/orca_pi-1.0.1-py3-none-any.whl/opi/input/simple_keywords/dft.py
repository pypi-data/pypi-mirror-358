from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Dft",)


class Dft(SimpleKeywordBox):
    """Enum to store all simple keywords of type Dft"""

    B3LYP3C = SimpleKeyword(
        "b3lyp3c"
    )  # DFT 3c methods, do not require dispersion correction or basis set
    B973C = SimpleKeyword(
        "b973c"
    )  # DFT 3c methods, do not require dispersion correction or basis set
    PBEH3C = SimpleKeyword(
        "pbeh3c"
    )  # DFT 3c methods, do not require dispersion correction or basis set
    WB97X3C = SimpleKeyword(
        "wb97x3c"
    )  # DFT 3c methods, do not require dispersion correction or basis set
    B3LYP_GCP_D3_6_31G_D = SimpleKeyword(
        "b3lyp-gcp-d3/6-31g(d)"
    )  # DFT like 3c methods, do not require dispersion correction or basis set
    B3LYP_GCP_D3_6_31GSTAR = SimpleKeyword(
        "b3lyp-gcp-d3/6-31g*"
    )  # DFT like 3c methods, do not require dispersion correction or basis set
    FOD = SimpleKeyword(
        "fod"
    )  # DFT with smearing for determining multireference character (TPSS/def2-TZVP, T = 5000 K)
    B1LYP = SimpleKeyword("b1lyp")  # DFT functional
    B1P = SimpleKeyword("b1p")  # DFT functional
    B1P86 = SimpleKeyword("b1p86")  # DFT functional
    B1PBE = SimpleKeyword("b1pbe")  # DFT functional
    B1PW = SimpleKeyword("b1pw")  # DFT functional
    B1PW91 = SimpleKeyword("b1pw91")  # DFT functional
    B2GP_PLYP = SimpleKeyword("b2gp-plyp")  # DFT functional
    B2K_PLYP = SimpleKeyword("b2k-plyp")  # DFT functional
    B2PLYP = SimpleKeyword("b2plyp")  # DFT functional
    B2T_PLYP = SimpleKeyword("b2t-plyp")  # DFT functional
    B3LYP = SimpleKeyword("b3lyp")  # DFT functional
    B3LYP_G = SimpleKeyword("b3lyp_g")  # DFT functional
    B3P = SimpleKeyword("b3p")  # DFT functional
    B3P86 = SimpleKeyword("b3p86")  # DFT functional
    B3PBE = SimpleKeyword("b3pbe")  # DFT functional
    B3PW = SimpleKeyword("b3pw")  # DFT functional
    B3PW91 = SimpleKeyword("b3pw91")  # DFT functional
    B97 = SimpleKeyword("b97")  # DFT functional
    B97_D = SimpleKeyword("b97-d")  # DFT functional
    B97_D3 = SimpleKeyword("b97-d3")  # DFT functional
    B97_D4 = SimpleKeyword("b97-d4")  # DFT functional
    B97M_D3BJ = SimpleKeyword("b97m-d3bj")  # DFT functional
    B97M_D4 = SimpleKeyword("b97m-d4")  # DFT functional
    B97M_V = SimpleKeyword("b97m-v")  # DFT functional
    BHANDHLYP = SimpleKeyword("bhandhlyp")  # DFT functional
    BHLYP = SimpleKeyword("bhlyp")  # DFT functional
    BLYP = SimpleKeyword("blyp")  # DFT functional
    BNULL = SimpleKeyword("bnull")  # DFT functional
    BP86 = SimpleKeyword("bp86")  # DFT functional
    BPBE = SimpleKeyword("bpbe")  # DFT functional
    BPW = SimpleKeyword("bpw")  # DFT functional
    BPW91 = SimpleKeyword("bpw91")  # DFT functional
    BVWN = SimpleKeyword("bvwn")  # DFT functional
    CAM_B3LYP = SimpleKeyword("cam-b3lyp")  # DFT functional
    DLPNO_B2GP_PLYP = SimpleKeyword("dlpno-b2gp-plyp")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_B2K_PLYP = SimpleKeyword("dlpno-b2k-plyp")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_B2PLYP = SimpleKeyword("dlpno-b2plyp")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_B2T_PLYP = SimpleKeyword("dlpno-b2t-plyp")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_DSD_BLYP = SimpleKeyword("dlpno-dsd-blyp")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_DSD_PBEB95 = SimpleKeyword(
        "dlpno-dsd-pbeb95"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_DSD_PBEP86 = SimpleKeyword(
        "dlpno-dsd-pbep86"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_KPR2SCAN50 = SimpleKeyword(
        "dlpno-kpr2scan50"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_MPW2PLYP = SimpleKeyword("dlpno-mpw2plyp")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_PBE_QIDH = SimpleKeyword("dlpno-pbe-qidh")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_PBE0_2 = SimpleKeyword("dlpno-pbe0-2")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_PBE0_DH = SimpleKeyword("dlpno-pbe0-dh")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_PR2SCAN50 = SimpleKeyword("dlpno-pr2scan50")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_PR2SCAN69 = SimpleKeyword("dlpno-pr2scan69")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_PWPB95 = SimpleKeyword("dlpno-pwpb95")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_R2SCAN_CIDH = SimpleKeyword(
        "dlpno-r2scan-cidh"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_R2SCAN_QIDH = SimpleKeyword(
        "dlpno-r2scan-qidh"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_R2SCAN0_2 = SimpleKeyword("dlpno-r2scan0-2")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_R2SCAN0_DH = SimpleKeyword(
        "dlpno-r2scan0-dh"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_RSX_0DH = SimpleKeyword("dlpno-rsx-0dh")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_RSX_QIDH = SimpleKeyword("dlpno-rsx-qidh")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SCS_B2GP_PLYP21 = SimpleKeyword(
        "dlpno-scs-b2gp-plyp21"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SCS_PBE_QIDH = SimpleKeyword(
        "dlpno-scs-pbe-qidh"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SCS_RSX_QIDH = SimpleKeyword(
        "dlpno-scs-rsx-qidh"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SCS_WB2GP_PLYP = SimpleKeyword(
        "dlpno-scs-wb2gp-plyp"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SCS_WB88PP86 = SimpleKeyword(
        "dlpno-scs-wb88pp86"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SCS_WPBEPP86 = SimpleKeyword(
        "dlpno-scs-wpbepp86"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SCS_SOS_B2PLYP21 = SimpleKeyword(
        "dlpno-scs/sos-b2plyp21"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SCS_SOS_WB2PLYP = SimpleKeyword(
        "dlpno-scs/sos-wb2plyp"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SOS_B2GP_PLYP21 = SimpleKeyword(
        "dlpno-sos-b2gp-plyp21"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SOS_PBE_QIDH = SimpleKeyword(
        "dlpno-sos-pbe-qidh"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SOS_RSX_QIDH = SimpleKeyword(
        "dlpno-sos-rsx-qidh"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SOS_WB2GP_PLYP = SimpleKeyword(
        "dlpno-sos-wb2gp-plyp"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SOS_WB88PP86 = SimpleKeyword(
        "dlpno-sos-wb88pp86"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_SOS_WPBEPP86 = SimpleKeyword(
        "dlpno-sos-wpbepp86"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_WB2GP_PLYP = SimpleKeyword(
        "dlpno-wb2gp-plyp"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_WB2PLYP = SimpleKeyword("dlpno-wb2plyp")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_WB88PP86 = SimpleKeyword("dlpno-wb88pp86")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_WB97M_2 = SimpleKeyword("dlpno-wb97m(2)")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_WB97X_2 = SimpleKeyword("dlpno-wb97x-2")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_WB97X_2_TQZ = SimpleKeyword(
        "dlpno-wb97x-2(tqz)"
    )  # Double-hybrid DFT with DLPNO approximation
    DLPNO_WPBEPP86 = SimpleKeyword("dlpno-wpbepp86")  # Double-hybrid DFT with DLPNO approximation
    DLPNO_WPR2SCAN50 = SimpleKeyword(
        "dlpno-wpr2scan50"
    )  # Double-hybrid DFT with DLPNO approximation
    DSD_BLYP = SimpleKeyword("dsd-blyp")  # DFT functional
    DSD_PBEB95 = SimpleKeyword("dsd-pbeb95")  # DFT functional
    DSD_PBEP86 = SimpleKeyword("dsd-pbep86")  # DFT functional
    G1LYP = SimpleKeyword("g1lyp")  # DFT functional
    G1P = SimpleKeyword("g1p")  # DFT functional
    G3LYP = SimpleKeyword("g3lyp")  # DFT functional
    G3P = SimpleKeyword("g3p")  # DFT functional
    GLYP = SimpleKeyword("glyp")  # DFT functional
    GP = SimpleKeyword("gp")  # DFT functional
    HFLDA = SimpleKeyword("hflda")  # DFT functional
    HFS = SimpleKeyword("hfs")  # DFT functional
    KPR2SCAN50 = SimpleKeyword("kpr2scan50")  # DFT functional
    LB94 = SimpleKeyword("lb94")  # DFT functional
    LC_BLYP = SimpleKeyword("lc-blyp")  # DFT functional
    LC_PBE = SimpleKeyword("lc-pbe")  # DFT functional
    LDA = SimpleKeyword("lda")  # DFT functional
    LRC_PBE = SimpleKeyword("lrc-pbe")  # DFT functional
    LSD = SimpleKeyword("lsd")  # DFT functional
    M06 = SimpleKeyword("m06")  # DFT functional
    M062X = SimpleKeyword("m062x")  # DFT functional
    M06L = SimpleKeyword("m06l")  # DFT functional
    MPW1LYP = SimpleKeyword("mpw1lyp")  # DFT functional
    MPW1PW = SimpleKeyword("mpw1pw")  # DFT functional
    MPW2PLYP = SimpleKeyword("mpw2plyp")  # DFT functional
    MPWLYP = SimpleKeyword("mpwlyp")  # DFT functional
    MPWPW = SimpleKeyword("mpwpw")  # DFT functional
    O3LYP = SimpleKeyword("o3lyp")  # DFT functional
    OLYP = SimpleKeyword("olyp")  # DFT functional
    OPBE = SimpleKeyword("opbe")  # DFT functional
    PBE = SimpleKeyword("pbe")  # DFT functional
    PBE_QIDH = SimpleKeyword("pbe-qidh")  # DFT functional
    PBE0 = SimpleKeyword("pbe0")  # DFT functional
    PBE0_2 = SimpleKeyword("pbe0-2")  # DFT functional
    PBE0_DH = SimpleKeyword("pbe0-dh")  # DFT functional
    PR2SCAN50 = SimpleKeyword("pr2scan50")  # DFT functional
    PR2SCAN69 = SimpleKeyword("pr2scan69")  # DFT functional
    PW1PW = SimpleKeyword("pw1pw")  # DFT functional
    PW6B95 = SimpleKeyword("pw6b95")  # DFT functional
    PW86PBE = SimpleKeyword("pw86pbe")  # DFT functional
    PW91 = SimpleKeyword("pw91")  # DFT functional
    PW91_0 = SimpleKeyword("pw91_0")  # DFT functional
    PWLDA = SimpleKeyword("pwlda")  # DFT functional
    PWP = SimpleKeyword("pwp")  # DFT functional
    PWP1 = SimpleKeyword("pwp1")  # DFT functional
    PWPB95 = SimpleKeyword("pwpb95")  # DFT functional
    R2SCAN = SimpleKeyword("r2scan")  # DFT functional
    R2SCAN_3C = SimpleKeyword("r2scan-3c")  # DFT functional
    R2SCAN_CIDH = SimpleKeyword("r2scan-cidh")  # DFT functional
    R2SCAN_QIDH = SimpleKeyword("r2scan-qidh")  # DFT functional
    R2SCAN0 = SimpleKeyword("r2scan0")  # DFT functional
    R2SCAN0 = SimpleKeyword("r2scan0")  # DFT functional
    R2SCAN0_2 = SimpleKeyword("r2scan0-2")  # DFT functional
    R2SCAN0_DH = SimpleKeyword("r2scan0-dh")  # DFT functional
    R2SCAN50 = SimpleKeyword("r2scan50")  # DFT functional
    R2SCANH = SimpleKeyword("r2scanh")  # DFT functional
    REVDOD_PBEP86_D4_2021 = SimpleKeyword("revdod-pbep86-d4/2021")  # DFT functional
    REVDOD_PBEP86_2021 = SimpleKeyword("revdod-pbep86/2021")  # DFT functional
    REVDSD_PBEP86_D4_2021 = SimpleKeyword("revdsd-pbep86-d4/2021")  # DFT functional
    REVDSD_PBEP86_2021 = SimpleKeyword("revdsd-pbep86/2021")  # DFT functional
    REVPBE = SimpleKeyword("revpbe")  # DFT functional
    REVPBE0 = SimpleKeyword("revpbe0")  # DFT functional
    REVPBE38 = SimpleKeyword("revpbe38")  # DFT functional
    REVTPSS = SimpleKeyword("revtpss")  # DFT functional
    RPBE = SimpleKeyword("rpbe")  # DFT functional
    RPW86PBE = SimpleKeyword("rpw86pbe")  # DFT functional
    RSCAN = SimpleKeyword("rscan")  # DFT functional
    RSX_0DH = SimpleKeyword("rsx-0dh")  # DFT functional
    RSX_QIDH = SimpleKeyword("rsx-qidh")  # DFT functional
    SCANFUNC = SimpleKeyword("scanfunc")  # DFT functional
    SCS_B2GP_PLYP21 = SimpleKeyword("scs-b2gp-plyp21")  # DFT functional
    SCS_PBE_QIDH = SimpleKeyword("scs-pbe-qidh")  # DFT functional
    SCS_RSX_QIDH = SimpleKeyword("scs-rsx-qidh")  # DFT functional
    SCS_WB2GP_PLYP = SimpleKeyword("scs-wb2gp-plyp")  # DFT functional
    SCS_WB88PP86 = SimpleKeyword("scs-wb88pp86")  # DFT functional
    SCS_WPBEPP86 = SimpleKeyword("scs-wpbepp86")  # DFT functional
    SCS_SOS_B2PLYP21 = SimpleKeyword("scs/sos-b2plyp21")  # DFT functional
    SCS_SOS_WB2PLYP = SimpleKeyword("scs/sos-wb2plyp")  # DFT functional
    SOS_B2GP_PLYP21 = SimpleKeyword("sos-b2gp-plyp21")  # DFT functional
    SOS_PBE_QIDH = SimpleKeyword("sos-pbe-qidh")  # DFT functional
    SOS_RSX_QIDH = SimpleKeyword("sos-rsx-qidh")  # DFT functional
    SOS_WB2GP_PLYP = SimpleKeyword("sos-wb2gp-plyp")  # DFT functional
    SOS_WB88PP86 = SimpleKeyword("sos-wb88pp86")  # DFT functional
    SOS_WPBEPP86 = SimpleKeyword("sos-wpbepp86")  # DFT functional
    TPSS = SimpleKeyword("tpss")  # DFT functional
    TPSS0 = SimpleKeyword("tpss0")  # DFT functional
    TPSSH = SimpleKeyword("tpssh")  # DFT functional
    VWN = SimpleKeyword("vwn")  # DFT functional
    VWN3 = SimpleKeyword("vwn3")  # DFT functional
    VWN5 = SimpleKeyword("vwn5")  # DFT functional
    WB2GP_PLYP = SimpleKeyword("wb2gp-plyp")  # DFT functional
    WB2PLYP = SimpleKeyword("wb2plyp")  # DFT functional
    WB88PP86 = SimpleKeyword("wb88pp86")  # DFT functional
    WB97 = SimpleKeyword("wb97")  # DFT functional
    WB97M_D3BJ = SimpleKeyword("wb97m-d3bj")  # DFT functional
    WB97M_D4 = SimpleKeyword("wb97m-d4")  # DFT functional
    WB97M_D4REV = SimpleKeyword("wb97m-d4rev")  # DFT functional
    WB97M_V = SimpleKeyword("wb97m-v")  # DFT functional
    WB97M_2 = SimpleKeyword("wb97m(2)")  # DFT functional
    WB97X = SimpleKeyword("wb97x")  # DFT functional
    WB97X_2 = SimpleKeyword("wb97x-2")  # DFT functional
    WB97X_2_TQZ = SimpleKeyword("wb97x-2(tqz)")  # DFT functional
    WB97X_D3 = SimpleKeyword("wb97x-d3")  # DFT functional
    WB97X_D3BJ = SimpleKeyword("wb97x-d3bj")  # DFT functional
    WB97X_D4 = SimpleKeyword("wb97x-d4")  # DFT functional
    WB97X_D4REV = SimpleKeyword("wb97x-d4rev")  # DFT functional
    WB97X_V = SimpleKeyword("wb97x-v")  # DFT functional
    WPBEPP86 = SimpleKeyword("wpbepp86")  # DFT functional
    WPR2SCAN50 = SimpleKeyword("wpr2scan50")  # DFT functional
    WR2SCAN = SimpleKeyword("wr2scan")  # DFT functional
    X3LYP = SimpleKeyword("x3lyp")  # DFT functional
    XHF = SimpleKeyword("xhf")  # DFT functional
    XLYP = SimpleKeyword("xlyp")  # DFT functional
