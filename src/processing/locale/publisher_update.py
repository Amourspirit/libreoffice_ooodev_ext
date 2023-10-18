from __future__ import annotations
from typing import Dict, cast, NamedTuple, List, TypedDict
from pathlib import Path
import toml
from lxml import etree
from ... import file_util
from ...config import Config
from ..token import Token


from .publisher import PublisherT, Element, Publisher


class PublisherUpdate(Publisher):
    """Reads Locale descriptions from pyproject.toml and writes them to update.xml."""

    def _get_xml_path(self) -> Path:
        return self._config.root_path / self._config.dist_dir_name / self._config.update_file
