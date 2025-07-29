# Installing OPI

OPI provides a Python library for accessing ORCA and processing its results. Currently, it is distributed via [PyPI](https://pypi.org/project/orca-pi/) and [GitHub](https://github.com/faccts/opi).

OPI can either be installed directly from PyPI:

```
pip install orca-pi
```

or from GitHub:

```
git clone https://github.com/faccts/opi.git
cd opi
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install .
```

In order to use OPI properly we recommend to install it in a _venv_ environment.

## ORCA and Open MPI

OPI requires for most of its functionality that ORCA is installed on the host machine.
ORCA has to be obtained separately from our [download portal](https://www.faccts.de/orca/) (commercial and academic) or from the [ORCA Forum](https://orcaforum.kofo.mpg.de) (academic).
For parallel calculations also [Open MPI](https://www.open-mpi.org/) is required.
For most modern operating system Open MPI can usually be installed directly with the systems package manager.
Otherwise, a suitable version has be obtained and compiled from their website.

**Note that OPI is first introduced with ORCA 6.1 and is not compatible with earlier versions.
The minimal supported ORCA version is always stored in [ORCA_MINIMAL_VERSION](https://github.com/faccts/opi/blob/main/src/opi/__init__.py)**


## Config File

ORCA and Open MPI can be either be passed to OPI via the system path (`$PATH` and `$LD_LIBRARY_PATH`) or via a config file.
The config file should be located at `$XDG_CONFIG_HOME/opi/config.toml` (usually `$XDG_CONFIG_HOME` points to `$HOME/.config`).

The `config.toml` file should contain the absolute path to the ORCA and Open MPI base folders.
Where base folders mean the parent folder that contains the respective `bin/` and `lib/` folders.

```
ORCA_PATH = "/path/to/orca/"
# > Path to Open MPI installed with `apt`
MPI_PATH = "/usr"
```
