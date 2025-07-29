"""
This sub-package contains all modules and classes meant for ORCA input handling.
Those are namely:
    * `arbitrary_string`: Allows injection of arbitrary strings into the ORCA input.
    * `blocks` and `simple_keywords`: which hold the Python objects of the ORCA's simple keywords (those starting with "!") and block options (those starting with `%`).
    * `core`: Contains the central `Input` class, which is the glue between the three former mentioned objects.
    * `structures`: Contains classes to represent basic structures and structure files.
"""

from opi.input import blocks as blocks
from opi.input import simple_keywords as simple_keywords
from opi.input import structures as structures
from opi.input.arbitrary_string import ArbitraryString, ArbitraryStringPos
from opi.input.core import Input

__all__ = [
    "blocks",
    "simple_keywords",
    "structures",
    "ArbitraryStringPos",
    "ArbitraryString",
    "Input",
]
