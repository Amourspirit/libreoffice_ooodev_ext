from __future__ import annotations
from typing import cast, Dict, List
from pathlib import Path
import json
import toml

from oxt.___lo_pip___.ver.req_version import ReqVersion
from ..meta.singleton import Singleton
from ..config import Config
from .token import Token


class JsonConfig(metaclass=Singleton):
    """Singleton Class the Config Json."""

    def __init__(self) -> None:
        self._config = Config()
        self._cfg = toml.load(self._config.toml_path)
        self._requirements = cast(Dict[str, str], self._cfg["tool"]["oxt"]["requirements"])
        try:
            self._zip_preinstall_pure = cast(bool, self._cfg["tool"]["oxt"]["config"]["zip_preinstall_pure"])
        except Exception:
            self._zip_preinstall_pure = False
        try:
            self._auto_install_in_site_packages = cast(
                bool,
                self._cfg["tool"]["oxt"]["config"]["auto_install_in_site_packages"],
            )
        except Exception:
            self._auto_install_in_site_packages = False
        try:
            self._install_wheel = cast(bool, self._cfg["tool"]["oxt"]["config"]["install_wheel"])
        except Exception:
            self._install_wheel = False
        try:
            self._window_timeout = int(self._cfg["tool"]["oxt"]["config"]["window_timeout"])
        except Exception:
            self._window_timeout = 5
        try:
            self._dialog_desktop_owned = cast(bool, self._cfg["tool"]["oxt"]["config"]["dialog_desktop_owned"])
        except Exception:
            self._dialog_desktop_owned = False

        try:
            self._default_locale = cast(bool, self._cfg["tool"]["oxt"]["config"]["default_locale"])
        except Exception:
            self._default_locale = ["en", "US"]
        # resource_dir_name
        try:
            self._resource_dir_name = cast(str, self._cfg["tool"]["oxt"]["config"]["resource_dir_name"])
        except Exception:
            self._resource_dir_name = "resources"
        try:
            self._resource_properties_prefix = cast(
                str, self._cfg["tool"]["oxt"]["config"]["resource_properties_prefix"]
            )
        except Exception:
            self._resource_properties_prefix = "pipstrings"

        try:
            self._isolate_windows = cast(List[str], self._cfg["tool"]["oxt"]["isolate"]["windows"])
        except Exception:
            self._isolate_windows = []

        try:
            self._sym_link_cpython = cast(bool, self._cfg["tool"]["oxt"]["config"]["sym_link_cpython"])
        except Exception:
            self._sym_link_cpython = False
        try:
            self._uninstall_on_update = cast(bool, self._cfg["tool"]["oxt"]["config"]["uninstall_on_update"])
        except Exception:
            self._uninstall_on_update = True

        try:
            self._install_on_no_uninstall_permission = cast(
                bool,
                self._cfg["tool"]["oxt"]["config"]["install_on_no_uninstall_permission"],
            )
        except Exception:
            self._install_on_no_uninstall_permission = True

        try:
            self._no_pip_remove = cast(list, self._cfg["tool"]["oxt"]["config"]["no_pip_remove"])
        except Exception:
            self._no_pip_remove = ["pip", "setuptools", "wheel"]

        try:
            self._unload_after_install = cast(bool, self._cfg["tool"]["oxt"]["config"]["unload_after_install"])
        except Exception:
            self._unload_after_install = True

        try:
            self._extension_version = cast(str, self._cfg["project"]["version"])
        except Exception:
            self._extension_version = ""

        # region Requirements Rule
        # Access a specific table
        try:
            self._py_packages = cast(List[Dict[str, str]], self._cfg["tool"]["oxt"]["py_packages"])
        except Exception:
            self._py_packages = []
        # endregion Requirements Rule

        # region Project Specific
        self._package_name = cast(str, self._cfg["tool"]["oxt"]["config"]["package_name"])
        # endregion Project Specific

        self._validate()
        self._warnings()

    def update_json_config(self, json_config_path: Path) -> None:
        """Read and updates the config.json file."""
        with open(json_config_path, "r") as f:
            json_config = json.load(f)
        token = Token()
        json_config["py_pkg_dir"] = token.get_token_value("py_pkg_dir")
        json_config["lo_identifier"] = token.get_token_value("lo_identifier")
        json_config["lo_implementation_name"] = token.get_token_value("lo_implementation_name")
        json_config["oxt_name"] = token.get_token_value("oxt_name")
        json_config["lo_pip"] = token.get_token_value("lo_pip")

        json_config["zipped_preinstall_pure"] = self._zip_preinstall_pure
        json_config["auto_install_in_site_packages"] = self._auto_install_in_site_packages
        json_config["install_wheel"] = self._install_wheel
        json_config["window_timeout"] = self._window_timeout
        json_config["dialog_desktop_owned"] = self._dialog_desktop_owned
        json_config["default_locale"] = self._default_locale
        json_config["resource_dir_name"] = self._resource_dir_name
        json_config["resource_properties_prefix"] = self._resource_properties_prefix
        json_config["isolate_windows"] = self._isolate_windows
        json_config["sym_link_cpython"] = self._sym_link_cpython
        json_config["uninstall_on_update"] = self._uninstall_on_update
        json_config["unload_after_install"] = self._unload_after_install
        # json_config["log_pip_installs"] = self._log_pip_installs
        # update the requirements
        json_config["requirements"] = self._requirements
        json_config["has_locals"] = self._config.has_locals
        json_config["no_pip_remove"] = self._no_pip_remove
        json_config["install_on_no_uninstall_permission"] = self._install_on_no_uninstall_permission
        json_config["extension_version"] = self._extension_version

        # region Requirements Rule
        json_config["py_packages"] = self._py_packages
        # endregion Requirements Rule

        # region Project Specific
        json_config["package_name"] = self._package_name
        # endregion Project Specific

        # save the file
        with open(json_config_path, "w", encoding="utf-8") as f:
            json.dump(json_config, f, indent=4)

    def _validate(self) -> None:
        """Validate"""
        assert isinstance(self._requirements, dict), "requirements must be a dict"
        assert isinstance(self._zip_preinstall_pure, bool), "zip_preinstall_pure must be a bool"
        assert isinstance(self._auto_install_in_site_packages, bool), "auto_install_in_site_packages must be a bool"
        assert isinstance(self._install_wheel, bool), "install_wheel must be a bool"
        assert isinstance(self._window_timeout, int), "window_timeout must be an int"
        assert isinstance(self._dialog_desktop_owned, bool), "dialog_desktop_owned must be a bool"
        assert isinstance(self._default_locale, list), "default_locale must be a list"
        assert len(self._default_locale) > 0, "default_locale must have at least 1 elements"
        assert len(self._default_locale) < 4, "default_locale must have no more then three elements"
        assert isinstance(self._resource_dir_name, str), "resource_dir_name must be a string"
        assert len(self._resource_dir_name) > 0, "resource_dir_name must not be an empty string"
        assert isinstance(self._resource_properties_prefix, str), "resource_properties_prefix must be a string"
        assert len(self._resource_properties_prefix) > 0, "resource_properties_prefix must not be an empty string"
        assert isinstance(self._sym_link_cpython, bool), "sym_link_cpython must be a bool"
        assert isinstance(self._unload_after_install, bool), "unload_after_install must be a bool"
        assert isinstance(self._no_pip_remove, list), "no_pip_remove must be a list"
        assert isinstance(
            self._install_on_no_uninstall_permission, bool
        ), "_install_on_no_uninstall_permission must be a bool"
        assert self._extension_version.count(".") == 2, "extension_version must contain two periods"

        # region Requirements Rule
        platforms = {"linux", "macos", "win", "flatpak", "snap", "all"}
        restrictions = {"<", "<=", "==", "!=", ">", ">=", "^", "~", "~="}
        for pkg in self._py_packages:
            assert isinstance(pkg, dict), "py_packages must be a list of dicts"
            assert "name" in pkg, "py_packages must contain a 'name' key"
            assert "version" in pkg, "py_packages must contain a 'version' key"
            assert isinstance(pkg["name"], str), "py_packages name must be a string"
            assert isinstance(pkg["version"], str), "py_packages ver must be a string"
            if "platforms" in pkg:
                assert isinstance(pkg["platforms"], list), "py_packages platforms must be a list"
                for platform in pkg["platforms"]:
                    assert isinstance(platform, str), "py_packages platforms must be a list of strings"
                    assert (
                        platform in platforms
                    ), "py_packages platforms must be in ['linux', 'macos', 'win', 'flatpak', 'snap', 'all']"

            if "ignore_platforms" in pkg:
                assert isinstance(pkg["ignore_platforms"], list), "py_packages platforms must be a list"
                for platform in pkg["ignore_platforms"]:
                    assert isinstance(platform, str), "py_packages ignore_platforms must be a list of strings"
                    assert (
                        platform in platforms
                    ), "py_packages ignore_platforms must be in ['linux', 'macos', 'win', 'flatpak', 'snap', 'all']"
            if "python_versions" in pkg:
                assert isinstance(pkg["python_versions"], list), "py_packages python_versions must be a list"
                for py_ver in pkg["python_versions"]:
                    assert isinstance(py_ver, str), "py_packages python_versions must be a list of strings"
                    assert len(py_ver) != 0, "py_packages python_versions must be not be an empty string"
                    try:
                        # validate python version by converting to ReqVersion
                        py_ver = ReqVersion(py_ver)
                    except Exception as err:
                        raise Exception(f"Error in py_packages python_versions: {err}") from err

            if "restriction" in pkg:
                assert isinstance(pkg["restriction"], str), "py_packages python_versions must be a list"
                assert (
                    pkg["restriction"] in restrictions
                ), "py_packages restriction must be in ['<', '<=', '==', '!=', '>', '>=', '^', '~', '~=']"

        # endregion Requirements Rule

    def _warnings(self) -> None:
        warnings = []
        token = Token()
        dist_dir = cast(str, self._cfg["tool"]["oxt"]["config"]["dist_dir"])
        log_level = str(token.get_token_value("log_level"))
        log_format = str(token.get_token_value("log_format"))

        if dist_dir == "tmp_dist":
            warnings.append("'tool.oxt.config.dist_dir' is set to the default value of 'tmp_dist'.")
        if log_level != "INFO":
            warnings.append(f"'tool.oxt.config.log_level' is set to '{log_level}'. Set to INFO for production.")
        if "indent_str" in log_format:
            warnings.append(
                "'tool.oxt.config.log_format' contains 'indent_str'. This is for debugging. Remove for production."
            )
        if warnings:
            print("JsonConfig Warnings:")
            for warning in warnings:
                print(f"  {warning}")
            print()
