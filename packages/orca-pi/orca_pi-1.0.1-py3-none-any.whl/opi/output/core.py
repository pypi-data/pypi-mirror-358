"""
This module contains the main class for output handling.
It's mostly based on the ORCA's two JSONs files.
"""

import json
from pathlib import Path
from typing import Any
from warnings import warn

from opi.execution.core import Runner
from opi.output.grepper.recipes import has_terminated_normally
from opi.output.models.json.gbw.gbw_results import GbwResults
from opi.output.models.json.property.property_results import (
    PropertyResults,
)
from opi.utils.misc import check_minimal_version, lowercase
from opi.utils.orca_version import OrcaVersion


class Output:
    """
    Class that handles of ORCA output, especially the `<basename>.json` `<basename>.property.json`

    Attributes
    ----------
    basename: str
        Basename of the job.
    working_dir: Path
        Optional path to the working directory.
    do_create_gbw_json: bool, default: False
        Switch that determines if gbw-json file is created if missing.
    do_create_property_json: PropertyResults
        Switch that determines if property-json file is created if missing.
    results_properties: PropertyResults
        Properties parsed from `property.json`.
        Should be preferred over `property_json_data`.
    results_gbw: GbwResults
        Data parsed from `<basename>.json`.
        Should be preferred over `gbw_json_data`.
    property_json_data: dict[str, Any]
        JSON tree read from `<basename>.property.json`.
    gbw_json_data: dict[str, Any]
        JSON tree of read from `<basename>.json`.
    do_redump_jsons: bool, default: False
        Redump JSONs files after parsing. This is mostly meant for debugging.
    """

    def __init__(
        self,
        basename: str,
        *,
        working_dir: Path | None = None,
        create_gbw_json: bool = False,
        create_property_json: bool = False,
        version_check: bool = True,
        parse: bool = False,
    ):
        """
        ORCA output parser that is mainly based on the JSON-property and JSON-GBW file.
        It can also read strings from the output file (if present).
        All files are determined based on the job basename given at initialization.

        Arguments
        ---------
        basename: str
            Basename of the job.
        working_dir: Path
            Optional path to the working directory.
        create_gbw_json: bool = False
            Whether the JSON gbw-file should be created by calling `orca_2json`, will not overwrite an existing JSON-file
            Usually, this is already done by `Calculator` if used.
        create_property_json: bool = False
            Whether the JSON property-file should be created by calling orca_2json,
            will not overwrite an existing JSON-file.
            Usually, this is already done by `Calculator` if used.
        version_check: bool, default: True
            If True, check if the ORCA version stored in JSON-property file is compliant with the minimal supported ORCA version of this interface.
            A warning is printed if the version check is not passed.
            If the version check runs into an error a ValueError is raised.
        parse: bool, default: False
            True: Create (if turned on by `create_gbw_json/create_property_json`) and parse JSONs files at the end of the initialization.
            False: Only return an Output object. In order to use the object to access the JSON data,
                   `Output.parse()` has to be called first.
        """
        self.basename = basename
        self.do_version_check = version_check

        self.working_dir = working_dir.expanduser().resolve() if working_dir else Path.cwd()
        if not self.working_dir.is_dir():
            raise FileNotFoundError(f"Working dir does not exist: {working_dir}")

        # // JSON PATHS
        self.gbw_json_file = self.get_file(".json")
        self.property_json_file = self.get_file(".property.json")

        # > // SWITCHES: CREATE JSON FILES
        self.do_create_gbw_json = create_gbw_json
        self.do_create_property_json = create_property_json

        # > // REDUMP JSON AFTER PARSING
        self.do_redump_jsons: bool = False

        # > // RAW JSON TREES
        self.gbw_json_data: dict[str, Any] | None = None
        self.property_json_data: dict[str, Any] | None = None

        # // PARSED JSON TREES
        self.results_properties: PropertyResults | None = None
        self.results_gbw: GbwResults | None = None

        # // CREATE AND PARSE JSONS FILES
        if parse:
            self.parse()

    def parse(self) -> None:
        """
        Create property- and gbw-JSON file (according to `do_create_property_json` and `self.do_create_gbw_json`)
        and parse them.
        """

        # // Create JSONs files
        if self.do_create_gbw_json:
            self.create_gbw_json()
        if self.do_create_property_json:
            self.create_property_json()

        # // PARSE JSONS
        self.gbw_json_data = self._process_json_file(self.gbw_json_file)
        self.property_json_data = self._process_json_file(self.property_json_file)

        # > `property_json_data` needs to be set
        if self.do_version_check:
            self.check_version()

        # // Property JSON
        self.results_properties = PropertyResults(**self.property_json_data)
        # // GBW JSON file
        self.results_gbw = GbwResults(**self.gbw_json_data)

        # > Redump JSON files
        if self.do_redump_jsons:
            self._redump_jsons()

    def _read_json(self, json_file: Path, /) -> dict[str, Any]:
        """
        Read a JSON file and return its JSON tree.

        Parameters
        ---------
        json_file: Path
            Path to the JSON file to be read.

        Returns
        -------
        dict[str, Any]
            The JSON tree.

        Raises
        ------
        FileNotFoundError
            If the Path leads to no file
        """

        if not json_file.is_file():
            raise FileNotFoundError(f"JSON file does not exist: {json_file}")

        with json_file.open() as f_json:
            json_data: dict[str, Any] = json.load(f_json)
            return json_data

    def _process_json_file(self, json_file: Path, /) -> dict[str, Any]:
        """
        Read the JSON file and convert all keys to lowercase.

        Parameters
        ----------
        json_file : Path
            Path to JSON file to be read.
        """

        json_data: dict[str, Any] = self._read_json(json_file)
        # > Convert all keys to lowercase.
        lowercase(json_data)
        return json_data

    def _redump_jsons(self) -> None:
        """Redump both JSON files as read and parse by `PropertyResults` and `GbwResults`."""

        assert self.gbw_json_file
        assert self.results_gbw
        redumped_gbw_json_file = self.gbw_json_file.with_suffix(".interface.json")
        self._dump_json(self.results_gbw, redumped_gbw_json_file)

        assert self.property_json_file
        assert self.results_properties
        redumped_property_json_file = self.property_json_file.with_suffix(".interface.json")
        self._dump_json(self.results_properties, redumped_property_json_file)

    def _dump_json(self, result: GbwResults | PropertyResults, json_file: Path, /) -> None:
        """
        Dump `GbwResults` or `PropertyResults` to a JSON file.

        Parameters
        ----------
        result : GbwResults | PropertyResults
            Results to be dumped.
        json_file : Path
            Path to JSON file to be written.
        """

        json_string: str = result.model_dump_json(indent=2)
        json_file.write_text(json_string)

    def get_file(self, suffix: str, /) -> Path:
        """
        Get path to file, by specifying file suffix (including the leading dot).
        Fullpath will be inferred from `self.working_dir` and `self.basename`.

        Parameters
        ----------
        suffix : str
            Suffix of file. Must include the leading dot.
        """
        return self.working_dir / (self.basename + suffix)

    def _get_version(self) -> "OrcaVersion":
        """Gets the ORCA version from the property-JSON file."""

        # > Path to property JSON needs to be set
        try:
            assert self.property_json_data
            return OrcaVersion.from_json(self.property_json_data)
        except AssertionError:
            raise ValueError(
                "Could not determine ORCA version, as JSON-property file has not been parsed."
            )
        except ValueError:
            raise

    def check_version(self) -> None:
        """
        Check if the version from the property-JSON file fits to minimally support ORCA version of the current OPI version.
        """
        try:
            version = self._get_version()
        except ValueError:
            warn("Could not determine ORCA version from JSON file. Subsequent error might occur.")
        else:
            if not check_minimal_version(version):
                raise RuntimeError(
                    f"JSON property file was created with unsupported ORCA version: {version}"
                )

    def _create_runner(self) -> "Runner":
        """Create a `Runner` object passing on `self.working_dir`."""
        return Runner(working_dir=self.working_dir)

    def create_gbw_json(self, *, force: bool = False, config: dict[str, Any] | None = None) -> None:
        """
        Thin-wrapper around `Runner.create_jsons()`.
        Creates the `<basename>.json` file.

        Parameters
        ----------
        force : bool, default = False
            Overwrite any existing ORCA GBW JSON file.
        config : dict[str | Any] | None, default = None
            Determine contents of gbw-json file.
            For details about the configuration refer to the ORCA manual "9.3.2 Configuration file"
        """
        runner = self._create_runner()
        runner.create_gbw_json(self.basename, config=config, force=force)

    def create_property_json(self, *, force: bool = False) -> None:
        """
        Thin-wrapper around `Runner.create_property_json()`.
        Create the `<basename>.property.json` file

        Parameters
        ----------
        force : bool, default = None
            Overwrite any existing ORCA property JSON file.
        """
        runner = self._create_runner()
        runner.create_property_json(self.basename, force=force)

    def create_jsons(self, *, force: bool = False) -> None:
        """
        Thin-wrapper around `Runner.create_jsons()`.
        Create the `<basename>.json` and the `<basename>.property.json` file

        Parameters
        ----------
        force : bool, default: None
            Overwrite any existing ORCA property and GBW JSON files.
        """
        runner = self._create_runner()
        runner.create_jsons(self.basename, force=force)

    def get_outfile(self) -> Path:
        """
        The full path to the ".out" file.
        """
        return self.get_file(".out")

    def terminated_normally(self) -> bool:
        """
        Determine if ORCA terminated normally, by looking for "ORCA TERMINATED NORMALLY" in the ".out" file.
        If the ".out" file does not exist, also return False.
        """
        outfile = self.get_outfile()
        try:
            return has_terminated_normally(outfile)
        except FileNotFoundError:
            return False
