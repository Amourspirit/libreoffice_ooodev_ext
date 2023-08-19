from __future__ import annotations
import os
import sys
import shutil
from typing import Set
from pathlib import Path

import toml
from ..meta.singleton import Singleton
from ..config import Config


class Packages(metaclass=Singleton):
    """Singleton Class the Packages."""

    def __init__(self) -> None:
        self._config = Config()
        cfg = toml.load(self._config.toml_path)
        self._pkg_names: Set[str] = set(cfg["tool"]["oxt"]["metadata"]["py_pkg_names"])
        self._pkg_files: Set[str] = set(cfg["tool"]["oxt"]["metadata"]["py_pkg_files"])
        self._venv_path = Path(self._get_virtual_env_path())
        major, minor, *_ = sys.version_info
        self._site_packages_path = self._venv_path / "lib" / f"python{major}.{minor}" / "site-packages"
        if not self._site_packages_path.exists():
            # windows
            self._site_packages_path = self._venv_path / "Lib" / "site-packages"
        if not self._site_packages_path.exists():
            raise FileNotFoundError("Unable to get Site Packages Path")

    # region Methods

    def _get_virtual_env_path(self) -> str:
        """
        Gets the Virtual Environment Path

        Returns:
            str: Virtual Environment Path
        """
        s_path = os.environ.get("VIRTUAL_ENV", None)
        if s_path is not None:
            return s_path
        raise FileNotFoundError("Unable to get Virtual Environment Path")

    def copy_packages(self, dst: str | Path) -> None:
        """Copies the packages to the build directory."""
        if isinstance(dst, str):
            dest = Path(dst)
        else:
            dest = dst

        for pkg_name in self._pkg_names:
            shutil.copytree(src=self.site_packages_path / pkg_name, dst=dest / pkg_name)

    def copy_files(self, dst: str | Path) -> None:
        """Copies the files to the build directory."""
        if isinstance(dst, str):
            dest = Path(dst)
        else:
            dest = dst

        for pkg_file in self._pkg_files:
            shutil.copy(src=self.site_packages_path / pkg_file, dst=dest / pkg_file)

    def clear_cache(self, dst: str | Path) -> None:
        """
        Recursively removes generic `__pycache__` .

        The `__pycache__` files are automatically created by python during the simulation.
        This function removes the generic files on simulation start and simulation end.
        """
        if isinstance(dst, str):
            dest = Path(dst)
        else:
            dest = dst
        del_dir = "__pycache__"
        if del_dir in os.listdir(dst):
            shutil.rmtree(dest / del_dir, ignore_errors=True)

        for dir in os.listdir(dest):
            dir = dest / dir
            if os.path.isdir(dir):
                self.clear_cache(dir)

    # endregion Methods

    # region Properties
    @property
    def venv_path(self) -> Path:
        """The Virtual Environment Path."""
        return self._venv_path

    @property
    def site_packages_path(self) -> Path:
        """The Site Packages Path."""
        return self._site_packages_path

    @property
    def pkg_names(self) -> Set[str]:
        """The Package Names."""
        return self._pkg_names

    @property
    def pkg_files(self) -> Set[str]:
        """The Package Files."""
        return self._pkg_files

    # endregion Properties
