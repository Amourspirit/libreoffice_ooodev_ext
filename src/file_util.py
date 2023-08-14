from __future__ import annotations
import os
import shutil
import zipfile
from pathlib import Path
from pathlib import Path
from typing import Iterable, List
import os
from contextlib import contextmanager


@contextmanager
def change_dir(directory):
    """
    A context manager that changes the current working directory to the specified directory
    temporarily and then changes it back when the context is exited.
    """
    current_dir = os.getcwd()
    os.chdir(directory)
    try:
        yield
    finally:
        os.chdir(current_dir)


def find_file_in_parent_dirs(filename: str, path: str = "") -> str:
    """
    Recursively searches parent directories for a file with the given filename.
    Returns the absolute path to the file if found, or None if not found.
    """
    if path is None:
        path = os.getcwd()

    file_path = os.path.join(path, filename)
    if os.path.exists(file_path):
        return os.path.abspath(file_path)

    parent_dir = os.path.abspath(os.path.join(path, os.pardir))
    if parent_dir == path:
        # We've reached the root directory and haven't found the file
        return ""

    return find_file_in_parent_dirs(filename, parent_dir)


def mkdirp(self, dest_dir):
    # Python ≥ 3.5
    if isinstance(dest_dir, Path):
        dest_dir.mkdir(parents=True, exist_ok=True)
    else:
        Path(dest_dir).mkdir(parents=True, exist_ok=True)


def find_files_matching_patterns(root_dir: str | Path, ext: Iterable[str]) -> List[str]:
    """
    Finds all files in the given directory and its subdirectories that match the patterns *.txt and *.xml.
    Returns a list of absolute file paths.

    Args:
        root_dir (str | Path): The root directory to search.
        ext (List[str]): The file extensions to search for.
    Returns:
        List[str]: A list of absolute file paths.
    """
    if isinstance(root_dir, str):
        root_path = Path(root_dir)
    else:
        root_path = root_dir
    if not root_path.exists():
        raise FileNotFoundError(f"Directory '{root_dir}' not found")
    if not ext:
        return []

    file_paths = []
    extensions = set([f".{e.lower()}" for e in ext])
    for file_path in root_path.glob("**/*"):
        if file_path.is_file() and (file_path.suffix in extensions):
            file_paths.append(str(file_path.absolute()))

    return file_paths


def read_file(file_path: str) -> str:
    """Read the contents of the given file and return it as a string."""
    with open(file_path, "r") as f:
        return f.read()


def write_string_to_file(file_path: str, content: str) -> None:
    """Write the given string to the specified file."""
    with open(file_path, "w") as f:
        f.write(content)


def zip_folder(folder: str | Path, base_name: str = "", dest_dir: str | Path = "") -> None:
    """
    Zips all files in the given folder to the specified zip file.

    Args:
        folder (str | Path): is a directory that will be the root directory of the archive;
        base_name (str): is the name of the file to create, minus any format-specific
            extension; 'format' is the archive format: one of "zip", "tar", "gztar",
            "bztar", or "xztar".  Or any other registered format.

    Returns:
        None
    """
    if isinstance(folder, str):
        folder_path = Path(folder)
    else:
        folder_path = folder
    if not folder_path.is_dir():
        raise ValueError(f"Expected folder, got '{folder_path}'")
    if not folder_path.is_absolute():
        folder_path = folder_path.absolute()
    if not folder_path.exists():
        raise FileNotFoundError(f"Folder '{folder_path}' not found")
    if not base_name:
        base_name = folder_path.name

    if isinstance(dest_dir, str):
        if dest_dir == "":
            dest_dir = folder_path.parent
        else:
            dest_dir = Path(dest_dir)
    else:
        dest_dir = dest_dir.absolute()

    if not dest_dir.is_dir():
        raise ValueError(f"Expected folder, got '{dest_dir}'")
    if not dest_dir.exists():
        raise FileNotFoundError(f"Folder '{dest_dir}' not found")

    with change_dir(dest_dir):
        shutil.make_archive(base_name, "zip", folder_path)
