from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Gcp",)


class Gcp(SimpleKeywordBox):
    """Enum to store all simple keywords of type Gcp"""

    GCP_DFT_631G_D = SimpleKeyword(
        "gcp(dft/631g(d))"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_DFT_631GSTAR = SimpleKeyword(
        "gcp(dft/631g*)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_DFT_631GD = SimpleKeyword(
        "gcp(dft/631gd)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_DFT_LANL = SimpleKeyword(
        "gcp(dft/lanl)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_DFT_MINIS = SimpleKeyword(
        "gcp(dft/minis)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_DFT_SV_P = SimpleKeyword(
        "gcp(dft/sv(p))"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_DFT_SV_P_H_C = SimpleKeyword(
        "gcp(dft/sv(p/h,c))"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_DFT_SV = SimpleKeyword(
        "gcp(dft/sv)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_DFT_SVP = SimpleKeyword(
        "gcp(dft/svp)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_DFT_SVX = SimpleKeyword(
        "gcp(dft/svx)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_DFT_TZ = SimpleKeyword(
        "gcp(dft/tz)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_FILE = SimpleKeyword(
        "gcp(file)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_HF_631G_D = SimpleKeyword(
        "gcp(hf/631g(d))"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_HF_631GSTAR = SimpleKeyword(
        "gcp(hf/631g*)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_HF_631GD = SimpleKeyword(
        "gcp(hf/631gd)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_HF_MINIS = SimpleKeyword(
        "gcp(hf/minis)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_HF_MINIX = SimpleKeyword(
        "gcp(hf/minix)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_HF_SV_P = SimpleKeyword(
        "gcp(hf/sv(p))"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_HF_SV_P_H_C = SimpleKeyword(
        "gcp(hf/sv(p/h,c))"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_HF_SV = SimpleKeyword(
        "gcp(hf/sv)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_HF_SVP = SimpleKeyword(
        "gcp(hf/svp)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_HF_SVX = SimpleKeyword(
        "gcp(hf/svx)"
    )  # Correction for basis set errors (Method/basis set dependent)
    GCP_HF_TZ = SimpleKeyword(
        "gcp(hf/tz)"
    )  # Correction for basis set errors (Method/basis set dependent)
