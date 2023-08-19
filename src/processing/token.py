from __future__ import annotations
from typing import cast, Dict
import toml
from ..meta.singleton import Singleton
from .. import file_util


class Token(metaclass=Singleton):
    """Singleton Class the tokens."""

    def __init__(self) -> None:
        toml_path = file_util.find_file_in_parent_dirs("pyproject.toml")
        cfg = toml.load(toml_path)

        tokens = cast(Dict[str, str], cfg["tool"]["oxt"]["token"])
        self._tokens: Dict[str, str] = {}
        for token, replacement in tokens.items():
            self._tokens[f"@{token}@"] = replacement
        self._tokens["@version@"] = str(cfg["tool"]["poetry"]["version"])
        self._tokens["@license@"] = str(cfg["tool"]["poetry"]["license"])
        self._tokens["@oxt_name@"] = str(cfg["tool"]["oxt"]["metadata"]["oxt_name"])
        self._tokens["@dist_dir@"] = str(cfg["tool"]["oxt"]["metadata"]["dist_dir"])
        for token, replacement in self._tokens.items():
            self._tokens[token] = self.process(replacement)

    # region Methods
    def process(self, text: str) -> str:
        """Processes the given text."""
        for token, replacement in self._tokens.items():
            text = text.replace(token, replacement)

        return text

    # endregion Methods

    # region Properties
    @property
    def tokens(self) -> Dict[str, str]:
        """The tokens."""
        return self._tokens

    # endregion Properties
