from opi.input.simple_keywords.base import (
    SimpleKeyword,
    SimpleKeywordBox,
)

__all__ = ("Miscellaneous",)


class Miscellaneous(SimpleKeywordBox):
    """Enum to store all simple keywords of type Miscellaneous"""

    ANGS = SimpleKeyword("angs")
    BOHRS = SimpleKeyword("bohrs")
    CHEAPINTS = SimpleKeyword("cheapints")
    KEEPDENS = SimpleKeyword("keepdens")
    KEEPDENSITY = SimpleKeyword("keepdensity")
    KEEPFOCK = SimpleKeyword("keepfock")
    KEEPINTS = SimpleKeyword("keepints")
    KEEPRESPDENSITY = SimpleKeyword("keeprespdensity")
    KEEPTRANSDENSITY = SimpleKeyword("keeptransdensity")
    LIBINT = SimpleKeyword("libint")  # Libint for Integral generation
    MASS2016 = SimpleKeyword("mass2016")
    NOCHEAPINTS = SimpleKeyword("nocheapints")
    NOKEEPDENS = SimpleKeyword("nokeepdens")
    NOKEEPDENSITY = SimpleKeyword("nokeepdensity")
    NOKEEPFOCK = SimpleKeyword("nokeepfock")
    NOKEEPINTS = SimpleKeyword("nokeepints")
    NOLIBINT = SimpleKeyword("nolibint")  # Libint for Integral generation
    NOREADINTS = SimpleKeyword("noreadints")
    NOSHARK = SimpleKeyword("noshark")  # Shark for integral generation
    NOSYM = SimpleKeyword("nosym")  # Symmetry keywords
    NOSYMMETRY = SimpleKeyword("nosymmetry")  # Symmetry keywords
    NOUSESHARK = SimpleKeyword("nouseshark")  # Shark for integral generation
    NOUSESYM = SimpleKeyword("nousesym")  # Symmetry keywords
    NOUSESYMMETRY = SimpleKeyword("nousesymmetry")  # Symmetry keywords
    NOXCFUN = SimpleKeyword("noxcfun")  # do not use Xcfun library
    PAL = SimpleKeyword("pal")  # Parallelization
    PAL16 = SimpleKeyword("pal16")  # Parallelization
    PAL16_4X4 = SimpleKeyword("pal16(4x4)")  # Parallelization
    PAL2 = SimpleKeyword("pal2")  # Parallelization
    PAL3 = SimpleKeyword("pal3")  # Parallelization
    PAL32 = SimpleKeyword("pal32")  # Parallelization
    PAL32_4X8 = SimpleKeyword("pal32(4x8)")  # Parallelization
    PAL32_8X4 = SimpleKeyword("pal32(8x4)")  # Parallelization
    PAL4 = SimpleKeyword("pal4")  # Parallelization
    PAL4_2X2 = SimpleKeyword("pal4(2x2)")  # Parallelization
    PAL5 = SimpleKeyword("pal5")  # Parallelization
    PAL6 = SimpleKeyword("pal6")  # Parallelization
    PAL64 = SimpleKeyword("pal64")  # Parallelization
    PAL64_8X8 = SimpleKeyword("pal64(8x8)")  # Parallelization
    PAL7 = SimpleKeyword("pal7")  # Parallelization
    PAL8 = SimpleKeyword("pal8")  # Parallelization
    PAL8_2X4 = SimpleKeyword("pal8(2x4)")  # Parallelization
    PAL8_4X2 = SimpleKeyword("pal8(4x2)")  # Parallelization
    PREFERC2V = SimpleKeyword("preferc2v")  # Symmetry keywords
    PREFERD2 = SimpleKeyword("preferd2")  # Symmetry keywords
    READINTS = SimpleKeyword("readints")
    RESCUE = SimpleKeyword("rescue")  # Try to rescue a calculation from an old orca version
    SCALEPC = SimpleKeyword("scalepc")  # Scale Pointcharges
    SHARK = SimpleKeyword("shark")  # Shark for integral generation
    USEC2V = SimpleKeyword("usec2v")  # Symmetry keywords
    USED2 = SimpleKeyword("used2")  # Symmetry keywords
    USESHARK = SimpleKeyword("useshark")  # Shark for integral generation
    USESYM = SimpleKeyword("usesym")  # Symmetry keywords
    USESYMMETRY = SimpleKeyword("usesymmetry")  # Symmetry keywords
    XCFUN = SimpleKeyword("xcfun")  # Use Xcfun library
    PAF = SimpleKeyword("paf")  # Bring molecule into its principle axis orientation
    ALLOWRHF = SimpleKeyword("allowrhf")  # AllowRHF for open-shell
    NOALLOWRHF = SimpleKeyword("noallowrhf")  # AllowRHF for open-shell
    DOEQ = SimpleKeyword("doeq")  # Do Eq for nuclear charges
    NOEQ = SimpleKeyword("noeq")  # Do not Eq for nuclear charges
    BPOP = SimpleKeyword("bpop")  # Use Boltzmann weighting in multiple xyz job
    NUMGRAD = SimpleKeyword("numgrad")  # Numerical gradient
    SURFCROSSNUMFREQ = SimpleKeyword("surfcrossnumfreq")  # Check for surface crossing frequency
    MECP_NUMFREQ = SimpleKeyword("mecp-numfreq")  # Numerical MECP freq
    NEARIR = SimpleKeyword("nearir")  # VPT2 analysis for nearIR
    VPT2 = SimpleKeyword("vpt2")  # VPT2 analysis
