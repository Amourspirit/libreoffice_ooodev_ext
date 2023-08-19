from __future__ import annotations
from typing import Set, Dict, Any, cast
from . import file_util
import toml
from pathlib import Path
from .meta.singleton import Singleton
from .processing.token import Token


class Config(metaclass=Singleton):
    """Singleton class for the project configuration."""

    def __init__(self) -> None:
        toml_path = file_util.find_file_in_parent_dirs("pyproject.toml")
        if not toml_path:
            raise FileNotFoundError("pyproject.toml not found")
        self._toml_path = Path(toml_path)
        self._root_path = self._toml_path.parent
        cfg = toml.load(self._toml_path)
        token = Token()
        cfg_meta: Dict[str, Any] = cfg["tool"]["oxt"]["metadata"]
        self._build_dir_name = token.process(cast(str, cfg_meta["build_dir"]))
        self._dist_dir_name = token.process(cast(str, cfg_meta["dist_dir"]))
        self._otx_name = token.process(cast(str, cfg_meta["oxt_name"]))
        self._update_file = token.process(cast(str, cfg_meta["update_file"]))
        self._ver_str = cast(str, cfg["tool"]["poetry"]["version"])
        self._license = cast(str, cfg["tool"]["poetry"]["license"])
        self._token_file_ext: Set[str] = set(cast(list, cfg_meta["token_file_ext"]))

    # region Properties
    @property
    def toml_path(self) -> Path:
        """The path to the pyproject.toml file."""
        return self._toml_path

    @property
    def root_path(self) -> Path:
        """The root path of the project."""
        return self._root_path

    @property
    def build_dir_name(self) -> str:
        """The name of the build directory."""
        return self._build_dir_name

    @property
    def dist_dir_name(self) -> str:
        """The name of the dist directory."""
        return self._dist_dir_name

    @property
    def otx_name(self) -> str:
        """The name of the oxt file."""
        return self._otx_name

    @property
    def ver_str(self) -> str:
        """The version string."""
        return self._ver_str

    @property
    def license(self) -> str:
        """The license."""
        return self._license

    @property
    def token_file_ext(self) -> Set[str]:
        """The file extensions of token files."""
        return self._token_file_ext

    @property
    def update_file(self) -> str:
        """The name of the update file."""
        return self._update_file

    # endregion Properties
