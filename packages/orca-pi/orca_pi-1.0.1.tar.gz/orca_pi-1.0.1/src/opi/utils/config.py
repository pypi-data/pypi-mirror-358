import tomllib
from pathlib import Path
from typing import Any, Literal, Protocol, cast

from platformdirs import site_config_path, user_config_dir

from opi.utils.misc import eprint, get_package_name, is_linux

# > Name of the package
PKG_NAME = get_package_name()


class _ConfigDir(Protocol):
    """Protocol for `user_config_dir`-like function for type checking."""

    def __call__(
        self,
        appname: str | None,  # noqa: F841
        appauthor: str | None | Literal[False],  # noqa: F841
        *args: list[Any],
        **kwargs: dict[str, Any],
    ) -> str: ...


def _get_config_file(dirname: Path | _ConfigDir, /) -> Path | None:
    """
    Parameters
    ----------
    dirname : Path | _ConfigDir
    """
    # > Get user config dir. Usually: ~/.config
    if isinstance(dirname, Path):
        config_dir = (dirname / PKG_NAME).resolve()
    else:
        config_dir = Path(dirname(PKG_NAME, False))
    # > Get config file.
    config_file = config_dir / "config.toml"
    # > Return None if file does not exist
    return config_file if config_file.is_file() else None


def _get_config_files() -> tuple[Path, ...] | tuple[()]:
    """
    Returns
    -------
    tuple[Path, ...] | tuple[()]
    """
    # > Order of dirs is important!
    dirs: list[Path | _ConfigDir] = [
        cast(_ConfigDir, site_config_path),
        cast(_ConfigDir, user_config_dir),
    ]
    # > Add '/etc/<PKG_NAME>' first if on Linux.
    if is_linux():
        dirs.insert(0, Path("/etc"))
    # > Get config files.
    config_files: list[Path] = []
    for d in dirs:
        config_file = _get_config_file(d)
        if config_file:
            config_files.append(config_file)
    return tuple(config_files)


def _read_config_file(filepath: Path, /, config: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Parameters
    ----------
    filepath : Path
    config : dict[str | Any] | None, default: None
    """
    if config is None:
        config = {}

    with filepath.open("rb") as f_conf:
        try:
            config.update(tomllib.load(f_conf))
        except tomllib.TOMLDecodeError:
            raise
        else:
            return config


def get_config() -> dict[str, Any] | None:
    # > Get config file
    config_files = _get_config_files()
    # > If exists. Load and return the config.
    if not config_files:
        return None
    # << END OF IF
    config: dict[str, Any] = {}
    for file in config_files:
        try:
            config = _read_config_file(file, config)
        except tomllib.TOMLDecodeError as err:
            eprint(f"Could not load config file:\n{err}\n")
            raise
    return config
