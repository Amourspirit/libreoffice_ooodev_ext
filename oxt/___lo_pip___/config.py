# coding: utf-8
# region Imports
from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Set, TYPE_CHECKING
import json
import os
import sys
import platform
import site

from .oxt_logger.logger_config import LoggerConfig
from .basic_config import BasicConfig
from .oxt_logger.oxt_logger import OxtLogger

if TYPE_CHECKING:
    from .lo_util import Session
    from .lo_util import Util
    from .info import ExtensionInfo
    from .settings.general_settings import GeneralSettings
# endregion Imports


# region Constants

OS = platform.system()
IS_WIN = OS == "Windows"
IS_MAC = OS == "Darwin"
IS_LINUX = OS == "Linux"

# endregion Constants

# region Config Class


class Config:
    """
    Singleton Configuration Class

    Generally speaking this class is only used internally.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):  # noqa: ANN204
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls, *args, **kwargs)
            cls._instance._is_init = False
            cls._instance._requirements_set = False
            cls._instance.__init__()
        if not cls._instance._requirements_set:
            # _set_requirements() needs VerRules which in turn needs packaging.
            # Because packaging is not available while the extension is being installed this is done here.
            # After extension is installed, packaging will be available.
            cls._instance._requirements_set = cls._instance._set_requirements(cls._instance._requirements)
        return cls._instance

    # region Init

    def __init__(self) -> None:
        if getattr(self, "_is_init", False):
            return
        if not TYPE_CHECKING:
            from .lo_util import Session
            from .info import ExtensionInfo
            from .lo_util import Util
            from .settings.general_settings import GeneralSettings

        logger_config = LoggerConfig()
        self._logger = OxtLogger(log_name=__name__)
        self._logger.debug("Initializing Config")
        try:
            self._log_file = logger_config.log_file
            self._log_name = logger_config.log_name
            self._log_format = logger_config.log_format
            self._basic_config = BasicConfig()
            self._logger.debug("Basic config initialized")
            self._requirements = self._basic_config.requirements
            self._requirements_set = self._set_requirements(self._requirements)
            generals_settings = GeneralSettings()
            self._logger.debug("General Settings initialized")
            self._url_pip = generals_settings.url_pip
            self._pip_wheel_url = generals_settings.pip_wheel_url
            self._test_internet_url = generals_settings.test_internet_url
            self._log_pip_installs = generals_settings.log_pip_installs
            self._show_progress = generals_settings.show_progress
            self._startup_event = generals_settings.startup_event
            self._delay_startup = generals_settings.delay_startup

            self._session = Session()
            self._extension_info = ExtensionInfo()
            self._auto_install_in_site_packages = self._basic_config.auto_install_in_site_packages
            if not self._auto_install_in_site_packages and os.getenv("DEV_CONTAINER", "") == "1":
                # if running in a dev container (Codespace)
                self._auto_install_in_site_packages = True
            self._log_level = logger_config.log_level
            self._os = platform.system()
            self._is_win = IS_WIN
            self._is_mac = IS_MAC
            self._is_linux = IS_LINUX
            self._is_app_image = bool(os.getenv("APPIMAGE", ""))
            self._is_flatpak = bool(os.getenv("FLATPAK_ID", ""))
            self._is_snap = bool(os.getenv("SNAP_INSTANCE_NAME", ""))
            self._site_packages = ""
            util = Util()

            # self._package_location = Path(file_util.get_package_location(self._lo_identifier, True))
            self._package_location = Path(self._extension_info.get_extension_loc(self.lo_identifier, True)).resolve()
            self._python_major_minor = self._get_python_major_minor()

            self._is_user_installed = False
            self._is_shared_installed = False
            self._is_bundled_installed = False
            self._set_extension_installs()

            if self._is_win:
                self._python_path = Path(self.join(util.config("Module"), "python.exe"))
                self._site_packages = self._get_windows_site_packages_dir()
            elif self._is_mac:
                self._python_path = Path(self.join(util.config("Module"), "..", "Resources", "python")).resolve()
                self._site_packages = self._get_mac_site_packages_dir()
            elif self._is_app_image:
                self._python_path = Path(self.join(util.config("Module"), "python"))
                self._site_packages = self._get_default_site_packages_dir()
            else:
                self._python_path = Path(sys.executable)
                if self._is_flatpak:
                    self._site_packages = self._get_flatpak_site_packages_dir()
                else:
                    self._site_packages = self._get_default_site_packages_dir()
        except Exception as err:
            self._logger.error(f"Error initializing config: {err}", exc_info=True)
            raise
        self._logger.debug("Config initialized")
        self._is_init = True

    # endregion Init

    # region Methods
    def _set_requirements(self, req: Dict[str, str]) -> bool:
        if self._basic_config.package_name not in req:
            self._logger.debug(
                "%s requirement not part of pyproject.toml tool.oxt.requirements",
                self._basic_config.package_name,
            )
        try:
            from .settings.options import Options
            from .ver.rules.ver_rules import VerRules
        except ImportError:
            return False

        options = Options()
        package_ver = options.package_requirement
        if not package_ver:
            self._logger.debug(
                "No requirement set in extension options for %s package",
                self._basic_config.package_name,
            )
            return True
        else:
            self._logger.debug(
                "Setting from extension options - %s requirement: '%s'",
                self._basic_config.package_name,
                package_ver,
            )
        ver_rules = VerRules()
        matched_rules = ver_rules.get_matched_rules(package_ver)
        ver_strings = []
        for rule in matched_rules:
            ver_strings.append(rule.get_versions_str())

        if ver_strings:
            txt_ver = ",".join(ver_strings)
            self._logger.debug(
                "Setting from LO options - %s requirement: '%s'",
                self._basic_config.package_name,
                txt_ver,
            )
            req[self._basic_config.package_name] = txt_ver
        else:
            self._logger.error(
                "Invalid %s requirement: %s",
                self._basic_config.package_name,
                package_ver,
            )
        return True

    def join(self, *paths: str) -> str:
        return str(Path(paths[0]).joinpath(*paths[1:]))

    def _set_extension_installs(self) -> None:
        details = self._extension_info.get_extension_details(self.lo_identifier)
        if details[0] is not None:
            self._is_user_installed = True
        if details[1] is not None:
            self._is_shared_installed = True
        if details[2] is not None:
            self._is_bundled_installed = True

    def _get_python_major_minor(self) -> str:
        return f"{sys.version_info.major}.{sys.version_info.minor}"

    def _get_shared_site_packages_dir(self) -> Path:
        # sourcery skip: class-extract-method
        packages = site.getsitepackages()
        for pkg in packages:
            if pkg.endswith("site-packages"):
                return Path(pkg).resolve()
        for pkg in packages:
            if pkg.endswith("dist-packages"):
                return Path(pkg).resolve()
        return Path(packages[0]).resolve()

    def _get_default_site_packages_dir(self) -> str:
        if self.is_shared_installed or self.is_bundled_installed:
            # if package has been installed for all users (root)
            site_packages = self._get_shared_site_packages_dir()
        else:
            if site.USER_SITE:
                site_packages = Path(site.USER_SITE).resolve()
            else:
                site_packages = Path.home() / f".local/lib/python{self.python_major_minor}/site-packages"
            site_packages.mkdir(parents=True, exist_ok=True)
        return str(site_packages)

    def _get_flatpak_site_packages_dir(self) -> str:
        # should never be all users
        sand_box = os.getenv("FLATPAK_SANDBOX_DIR", "") or str(
            Path.home() / ".var/app/org.libreoffice.LibreOffice/sandbox"
        )
        site_packages = Path(sand_box) / f"lib/python{self.python_major_minor}/site-packages"
        site_packages.mkdir(parents=True, exist_ok=True)
        return str(site_packages)

    def _get_mac_site_packages_dir(self) -> str:
        # sourcery skip: class-extract-method
        if self.is_shared_installed or self.is_bundled_installed:
            # if package has been installed for all users (root)
            site_packages = self._get_shared_site_packages_dir()
        else:
            if site.USER_SITE:
                site_packages = Path(site.USER_SITE).resolve()
            else:
                site_packages = (
                    Path.home() / f"Library/LibreOfficePython/{self.python_major_minor}/lib/python/site-packages"
                )
            site_packages.mkdir(parents=True, exist_ok=True)
        return str(site_packages)

    def _get_windows_site_packages_dir(self) -> str:
        # sourcery skip: class-extract-method
        if self.is_shared_installed or self.is_bundled_installed:
            # if package has been installed for all users (root)
            site_packages = self._get_shared_site_packages_dir()
        else:
            if site.USER_SITE:
                site_packages = Path(site.USER_SITE).resolve()
            else:
                site_packages = (
                    Path.home() / f"'/AppData/Roaming/Python/Python{self.python_major_minor}/site-packages'"
                )
            site_packages.mkdir(parents=True, exist_ok=True)
        return str(site_packages)

    # endregion Methods

    # region Properties
    @property
    def basic_config(self) -> BasicConfig:
        """
        Gets the basic config.
        """
        return self._basic_config

    @property
    def delay_startup(self) -> bool:
        """
        Gets the flag indicating if the startup should be delayed.
        """
        return self._delay_startup

    @property
    def default_locale(self) -> List[str]:
        """
        Gets the default locale such as ``['en', 'US']``.

        The value for this property can be set in pyproject.toml (tool.oxt.config.default_locale)

        This is the default locale to use if the locale is not set in the LibreOffice configuration.
        """
        return self._basic_config._default_locale

    @property
    def default_locale_str(self) -> str:
        """
        Gets the default locale as string separated by ``-`` such as ``en-US``.

        The value for this property can be set in pyproject.toml (tool.oxt.config.default_locale)

        This is the default locale to use if the locale is not set in the LibreOffice configuration.
        """
        return "-".join(self.default_locale)

    @property
    def url_pip(self) -> str:
        """
        String path such as ``https://bootstrap.pypa.io/get-pip.py``

        The value for this property can be set in pyproject.toml (tool.oxt.token.url_pip)
        """
        return self._url_pip
        # return self._basic_config.url_pip

    @property
    def test_internet_url(self) -> str:
        """
        String path such as ``https://www.google.com``

        The value for this property can be set in pyproject.toml (tool.oxt.token.test_internet_url)
        """
        return self._test_internet_url

    @property
    def python_path(self) -> Path:
        """
        Gets the path to the python executable.

        For some strange reason, on windows, the path can come back as 'soffice.bin' for 'sys.executable'.
        """
        return self._python_path

    @property
    def log_file(self) -> str:
        """
        Gets the name of the log file.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_file)
        """
        return self._log_file

    @property
    def log_name(self) -> str:
        """
        Gets the name of the log file.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_name)
        """
        return self._log_name

    @property
    def log_level(self) -> int:
        """
        Gets the log level.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_level)
        """
        return self._log_level

    @property
    def log_format(self) -> str:
        """
        Gets the log format.

        The value for this property can be set in pyproject.toml (tool.oxt.token.log_format)
        """
        return self._log_format

    @property
    def py_pkg_dir(self) -> str:
        """
        Gets the name of the directory where python packages are installed as a zip.

        The value for this property can be set in pyproject.toml (tool.oxt.token.py_pkg_dir)
        """
        return self._basic_config.py_pkg_dir

    @property
    def requirements(self) -> Dict[str, str]:
        """
        Gets the set of requirements.

        The value for this property can be set in pyproject.toml (tool.oxt.token.requirements)

        The key is the name of the package and the value is the version number.
        Example: {"requests": ">=2.25.1"}
        """
        return self._basic_config.requirements

    @property
    def zipped_preinstall_pure(self) -> bool:
        """
        Gets the flag indicating if pure python packages are be zipped.

        The value for this property can be set in pyproject.toml (tool.oxt.config.zip_preinstall_pure)

        If this is set to ``True`` then pure python packages will be zipped and installed as a zip file.
        """
        return self._basic_config.zipped_preinstall_pure

    @property
    def auto_install_in_site_packages(self) -> bool:
        """
        Gets the flag indicating if packages are installed in the site-packages directory set in this config.

        The value for this property can be set in pyproject.toml (tool.oxt.config.auto_install_in_site_packages)

        If this is set to ``True`` then packages will be installed in the site-packages directory if this config has the value set.

        Flatpak ignores this setting and always installs packages in the site-packages directory determined in this config.

        Note:
            When running in a dev container (Codespace), this value is always set to ``True``.
        """
        return self._auto_install_in_site_packages

    @property
    def dialog_desktop_owned(self) -> bool:
        """
        Gets the flag indicating if the dialog is owned by LibreOffice desktop window.

        The value for this property can be set in pyproject.toml (tool.oxt.config.dialog_desktop_owned)

        If this is set to ``True`` then the dialog is owned by the LibreOffice desktop window.
        """
        return self._basic_config._dialog_desktop_owned

    @property
    def is_linux(self) -> bool:
        """
        Gets the flag indicating if the operating system is Linux.
        """
        return self._is_linux

    @property
    def is_mac(self) -> bool:
        """
        Gets the flag indicating if the operating system is macOS.
        """
        return self._is_mac

    @property
    def is_win(self) -> bool:
        """
        Gets the flag indicating if the operating system is Windows.
        """
        return self._is_win

    @property
    def is_app_image(self) -> bool:
        """
        Gets the flag indicating if LibreOffice is running as an AppImage.
        """
        return self._is_app_image

    @property
    def is_flatpak(self) -> bool:
        """
        Gets the flag indicating if LibreOffice is running as a Flatpak.
        """
        return self._is_flatpak

    @property
    def is_snap(self) -> bool:
        """
        Gets the flag indicating if LibreOffice is running as a Snap.
        """
        return self._is_snap

    @property
    def is_user_installed(self) -> bool:
        """
        Gets the flag indicating if extension is installed as user.
        """
        return self._is_user_installed

    @property
    def is_shared_installed(self) -> bool:
        """
        Gets the flag indicating if extension is installed as shared.
        """
        return self._is_shared_installed

    @property
    def is_bundled_installed(self) -> bool:
        """
        Gets the flag indicating if extension is installed bundled with LibreOffice.
        """
        return self._is_bundled_installed

    @property
    def no_pip_remove(self) -> Set[str]:
        """
        Gets the pip packages that are not allowed to be removed.

        The value for this property can be set in pyproject.toml (tool.oxt.config.no_pip_remove)

        This is the packages that are not allowed to be removed by the installer.
        """
        return self._basic_config.no_pip_remove

    @property
    def os(self) -> str:
        """
        Gets the operating system.
        """
        return self._os

    @property
    def pip_wheel_url(self) -> str:
        """
        Gets the pip wheel url.

        May be empty string.
        """
        return self._pip_wheel_url

    @property
    def install_on_no_uninstall_permission(self) -> bool:
        """
        Gets the flag indicating if a package cannot be uninstalled due to permission error,
        then it will be installed anyway. This is usually the case when a package is installed
        in the system packages folder.
        """
        return self._basic_config.install_on_no_uninstall_permission

    @property
    def install_wheel(self) -> bool:
        """
        Gets the flag indicating if wheel should be installed.
        """
        return self._basic_config.install_wheel

    @property
    def lo_identifier(self) -> str:
        """
        Gets the LibreOffice identifier, such as, ``org.openoffice.extensions.ooopip``

        The value for this property can be set in pyproject.toml (tool.oxt.token.lo_identifier)
        """
        return self._basic_config.lo_identifier

    @property
    def lo_implementation_name(self) -> str:
        """
        Gets the LibreOffice implementation name, such as ``OooPipRunner``

        The value for this property can be set in pyproject.toml (tool.oxt.token.lo_implementation_name)
        """
        return self._basic_config.lo_implementation_name

    @property
    def python_major_minor(self) -> str:
        """
        Gets the python major minor version, such as ``3.9``
        """
        return self._python_major_minor

    @property
    def site_packages(self) -> str:
        """
        Gets the path to the site-packages directory. May be empty string.
        """
        return self._site_packages

    @property
    def session(self) -> Session:
        """
        Gets the LibreOffice session info.
        """
        return self._session

    @property
    def package_location(self) -> Path:
        """
        Gets the LibreOffice package location.
        """
        return self._package_location

    @property
    def oxt_name(self) -> str:
        """
        Gets the Otx name of the extension without the ``.otx`` extension.

        The value for this property can be set in pyproject.toml (tool.oxt.token.oxt_name)
        """
        return self._basic_config.oxt_name

    @property
    def extension_info(self) -> ExtensionInfo:
        """
        Gets the LibreOffice extension info.
        """
        return self._extension_info

    @property
    def log_pip_installs(self) -> bool:
        """
        Gets the flag indicating if pip installs should be logged.
        """
        return self._log_pip_installs

    @property
    def has_locals(self) -> bool:
        """
        Gets the flag indicating if the extension has local pip files to install.
        """
        return self._basic_config.has_locals

    @property
    def resource_dir_name(self) -> str:
        """
        Gets the resource directory name.

        The value for this property can be set in pyproject.toml (tool.oxt.config.resource_dir_name)

        This is the name of the directory containing the resource files.
        """
        return self._basic_config._resource_dir_name

    @property
    def resource_properties_prefix(self) -> str:
        """
        Gets the resource properties prefix.

        The value for this property can be set in pyproject.toml (tool.oxt.config.resource_properties_prefix)

        This is the prefix for the resource properties.
        """
        return self._basic_config._resource_properties_prefix

    @property
    def show_progress(self) -> bool:
        """
        Gets the flag indicating if the terminal should be shown.
        """
        return self._show_progress

    @property
    def startup_event(self) -> str:
        """
        Gets the startup event of the extension.

        The value for this property can be set in pyproject.toml (tool.oxt.token.startup_event)
        """
        return self._startup_event

    @property
    def uninstall_on_update(self) -> bool:
        """
        Gets the flag indicating if python packages should be uninstalled before updating.
        """
        return self.basic_config.uninstall_on_update

    @property
    def window_timeout(self) -> int:
        """
        Gets the window timeout value.

        The value for this property can be set in pyproject.toml (tool.oxt.config.window_timeout)

        This is the number of seconds to wait for the LibreOffice window to start before installing packages without requiring a LibreOffice window.
        """
        return self._basic_config.window_timeout

    @property
    def isolate_windows(self) -> Set[str]:
        """
        Gets the list of package that are to  be installed in 32 or 64 bit locations.

        The value for this property can be set in pyproject.toml (tool.oxt.isolate.windows)
        """
        return self._basic_config.isolate_windows

    @property
    def sym_link_cpython(self) -> bool:
        """
        Gets the flag indicating if CPython files should be symlinked on Linux AppImage and Mac OS.

        The value for this property can be set in pyproject.toml (tool.oxt.config.sym_link_cpython)

        If this is set to ``True`` then CPython will be symlinked on Linux AppImage and Mac OS.
        """
        return self._basic_config.sym_link_cpython

    @property
    def unload_after_install(self) -> bool:
        """
        Gets the flag indicating if the extension installer should unload after installation.
        """
        return self.basic_config.unload_after_install

    @property
    def extension_version(self) -> str:
        """
        Gets extension version.

        The value for this property can be set in pyproject.toml (tool.poetry.version)
        """
        return self._basic_config.extension_version

    @property
    def lo_pip_dir(self) -> str:
        """
        Gets the Main Library directory name for this extension.

        The value for this property can be set in pyproject.toml (tool.oxt.token.lo_pip)
        """
        return self._basic_config.lo_pip_dir

    # endregion Properties


# endregion Config Class
