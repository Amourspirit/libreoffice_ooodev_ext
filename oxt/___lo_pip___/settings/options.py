from __future__ import annotations

from .settings import Settings
from ..meta.singleton import Singleton
from ..lo_util.configuration import Configuration


class Options(metaclass=Singleton):
    """Singleton Class. Manages Load Settings for the extension."""

    def __init__(self) -> None:
        settings = Settings()
        self._configuration = Configuration()
        self._node_value = f"/{settings.lo_implementation_name}.Settings/Options"
        self._load_ooo_dev = bool(settings.current_settings.get("OptionLoadOooDev", False))
        self._package_requirement = str(settings.current_settings.get("PackageRequirement", ""))

    # region Properties
    @property
    def load_ooo_dev(self) -> bool:
        """
        Gets if OOO Dev Tools should be imported when LibreOffice starts.
        """
        return self._load_ooo_dev

    @property
    def package_requirement(self) -> str:
        """
        Gets the Package Requirement.
        """
        return self._package_requirement

    # endregion Properties
