"""
Location of fixtures for pytest must be listed here.

To define the location of module containing fixtures, the absolute path to that model
starting from the main package folder must be given.
"""

from pathlib import Path

# > Location of modules containing fixtures.
# >> Searching for Python modules which do no start with an underscore and converting file path to module path.
pytest_plugins = [
    str(filename).removesuffix(".py").replace("/", ".")
    for filename in Path("tests/fixtures").glob("*.py")
    if not filename.name.startswith("_")
]
