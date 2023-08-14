from __future__ import annotations
import os
import shutil
from .config import Config
from . import file_util
from .build_args import BuildArgs
from .processing.token import Token
from .processing.packages import Packages
from .processing.update import Update


class Build:
    """Builds the project."""

    def __init__(self, args: BuildArgs) -> None:
        self._config = Config()
        self._build_path = self._config.root_path / self._config.build_dir_name
        self._args = args
        self._src_path = self._config.root_path / args.oxt_src
        if not self._src_path.exists():
            raise FileNotFoundError(f"Oxt source directory '{self._src_path}' not found")
        self._dist_path = self._config.root_path / self._config.dist_dir_name
        self._dist_path.mkdir(parents=True, exist_ok=True)

    def build(self) -> None:
        """Builds the project."""
        if self._args.clean:
            self.clean()
        # self._ensure_build()
        self._copy_src_dest()
        if self._args.process_tokens:
            self._process_tokens()

        if self._args.process_py_packages:
            pythonpath = self._build_path / "pythonpath"
            if pythonpath.exists():
                shutil.rmtree(pythonpath)

            self._copy_py_packages()
            self._copy_py_files()
            self._clear_cache()
            self._zip_python_path()

        if self._args.make_dist:
            self._zip_build()
            self._process_update()

    def process_tokens(self, text: str) -> str:
        """Processes the tokens in the given text."""
        token = Token()
        return token.process(text)

    def clean(self) -> None:
        """Cleans the project."""
        if self._build_path.exists():
            shutil.rmtree(self._build_path)

    def _ensure_build(self) -> None:
        """Ensures the build directory exists."""
        if not self._build_path.exists():
            self._build_path.mkdir(parents=True, exist_ok=True)

    def _copy_src_dest(self) -> None:
        """Copies the source files to the build directory."""
        shutil.copytree(src=self._src_path, dst=self._build_path)

    def _process_tokens(self) -> None:
        """Processes the tokens in the dest files."""
        files = file_util.find_files_matching_patterns(self._build_path, self._config.token_file_ext)
        for file in files:
            text = file_util.read_file(file)
            text = self.process_tokens(text)
            file_util.write_string_to_file(file, text)

    def _copy_py_packages(self) -> None:
        """Copies the python packages to the build directory."""
        packages = Packages()
        packages.copy_packages(self._build_path / "pythonpath")

    def _copy_py_files(self) -> None:
        """Copies the python files to the build directory."""
        packages = Packages()
        packages.copy_files(self._build_path / "pythonpath")

    def _clear_cache(self) -> None:
        """Cleans the cache."""
        packages = Packages()
        packages.clear_cache(self._build_path / "pythonpath")

    def _zip_python_path(self) -> None:
        """Zips the python path."""
        pth = self._build_path / "pythonpath"
        file_util.zip_folder(folder=pth)
        shutil.rmtree(pth)

    def _zip_build(self) -> None:
        """Zips the build directory."""

        old_file = self._dist_path / f"{self._config.build_dir_name}.zip"
        new_file = self._dist_path / f"{self._config.otx_name}.oxt"
        if new_file.exists():
            os.remove(new_file)

        file_util.zip_folder(folder=self._build_path, dest_dir=self._dist_path)

        os.rename(old_file, new_file)

    def _process_update(self) -> None:
        """Processes the update file."""
        update = Update()
        update.process()
