"""
File I/O utilities for folder metadata.
"""

import json
import os
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from fm.utils.model import (
    FolderMetadata,
    FolderType,
    FOLDER_FILES,
    RepoMetadata,
    PlatformMetadata,
    ProjectsMetadata,
    ProjectMetadata,
)


def find_folder_file(
    directory: Path = None,
) -> Tuple[Optional[Path], Optional[FolderType]]:
    """
    Find the nearest .folder.* file in the given directory or its parents.

    Args:
        directory: Directory to start searching from (defaults to current directory)

    Returns:
        Tuple of (file_path, folder_type) or (None, None) if not found
    """
    if directory is None:
        directory = Path.cwd()

    directory = directory.resolve()

    # Check current directory for any .folder.* file
    for folder_type, file_name in FOLDER_FILES.items():
        file_path = directory / file_name
        if file_path.exists():
            return file_path, folder_type

    # If not found and not at root, check parent directory
    parent = directory.parent
    if parent == directory:  # At root
        return None, None

    return find_folder_file(parent)


def read_folder_metadata(file_path: Path) -> Optional[FolderMetadata]:
    """
    Read and parse folder metadata from a .folder.* file.

    Args:
        file_path: Path to the .folder.* file

    Returns:
        Parsed metadata or None if file doesn't exist or is invalid
    """
    if not file_path.exists():
        return None

    try:
        with open(file_path, "r") as f:
            content = f.read().strip()

        # Try YAML first, then fall back to JSON
        try:
            data = yaml.safe_load(content)
        except yaml.YAMLError:
            data = json.loads(content)

        # Determine the type and parse accordingly
        folder_type = data.get("type")
        if folder_type == "repo":
            return RepoMetadata(**data)
        elif folder_type == "platform":
            return PlatformMetadata(**data)
        elif folder_type == "projects":
            return ProjectsMetadata(**data)
        elif folder_type == "project":
            return ProjectMetadata(**data)
        else:
            return None
    except (json.JSONDecodeError, yaml.YAMLError, KeyError, FileNotFoundError):
        return None


def write_folder_metadata(
    file_path: Path, metadata: FolderMetadata, format: str = "yaml"
) -> bool:
    """
    Write folder metadata to a .folder.* file.

    Args:
        file_path: Path to the .folder.* file
        metadata: Metadata to write
        format: Output format ("yaml" or "json")

    Returns:
        True if successful, False otherwise
    """
    try:
        # Convert to dict using model_dump (Pydantic v2) or dict (fallback)
        if hasattr(metadata, "model_dump"):
            data = metadata.model_dump()
        else:
            data = metadata.dict()

        with open(file_path, "w") as f:
            if format.lower() == "yaml":
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(data, f, indent=2)
        return True
    except Exception:
        return False


def find_all_folder_files(
    root_dir: Path = None, folder_type: FolderType = None
) -> List[Path]:
    """
    Find all .folder.* files in the repository.

    Args:
        root_dir: Root directory to start searching from (defaults to current directory)
        folder_type: Optional filter for specific folder type

    Returns:
        List of paths to .folder.* files
    """
    if root_dir is None:
        root_dir = Path.cwd()

    result = []

    # If folder_type is specified, only look for that type
    if folder_type:
        file_name = FOLDER_FILES[folder_type]
        for path in root_dir.glob(f"**/{file_name}"):
            result.append(path)
    else:
        # Otherwise, look for all folder files
        for file_name in FOLDER_FILES.values():
            for path in root_dir.glob(f"**/{file_name}"):
                result.append(path)

    return result
