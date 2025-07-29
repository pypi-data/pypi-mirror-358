"""
Repository scanner for folder metadata.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from fm.utils.model import FolderType, FOLDER_FILES
from fm.utils.io import read_folder_metadata, find_all_folder_files


class FolderNode:
    """Represents a folder in the repository structure."""

    def __init__(self, path: Path, folder_type: Optional[FolderType] = None):
        self.path = path
        self.folder_type = folder_type
        self.metadata = None
        self.children = []
        self.parent = None

        # Load metadata if folder_type is provided
        if folder_type:
            file_path = path / FOLDER_FILES[folder_type]
            if file_path.exists():
                self.metadata = read_folder_metadata(file_path)

    def add_child(self, child: "FolderNode"):
        """Add a child node."""
        self.children.append(child)
        child.parent = self

    def __repr__(self):
        return f"FolderNode({self.path}, {self.folder_type})"


def scan_repository(root_dir: Path = None) -> Tuple[FolderNode, Dict[Path, FolderNode]]:
    """
    Scan the repository and build a tree of folder nodes.

    Args:
        root_dir: Root directory to start scanning from (defaults to current directory)

    Returns:
        Tuple of (root_node, node_map) where node_map maps paths to nodes
    """
    if root_dir is None:
        root_dir = Path.cwd()

    # Find all folder files
    folder_files = find_all_folder_files(root_dir)

    # Create nodes for each folder with metadata
    nodes = {}
    for file_path in folder_files:
        folder_path = file_path.parent
        folder_type = None

        # Determine folder type from file name
        for ft, fn in FOLDER_FILES.items():
            if file_path.name == fn:
                folder_type = ft
                break

        if folder_type:
            node = FolderNode(folder_path, folder_type)
            nodes[folder_path] = node

    # Build tree structure
    root_node = None

    # Sort paths by depth to ensure parents are processed before children
    sorted_paths = sorted(nodes.keys(), key=lambda p: len(p.parts))

    for path in sorted_paths:
        node = nodes[path]

        # If this is a repo node, it's the root
        if node.folder_type == FolderType.REPO:
            root_node = node
            continue

        # Find the closest parent with metadata
        parent_path = path.parent
        while parent_path not in nodes and parent_path != root_dir.parent:
            parent_path = parent_path.parent

        if parent_path in nodes:
            parent_node = nodes[parent_path]
            parent_node.add_child(node)

    return root_node, nodes


def find_repo_root(start_dir: Path = None) -> Optional[Path]:
    """
    Find the repository root by looking for .folder.repo file.

    Args:
        start_dir: Directory to start searching from (defaults to current directory)

    Returns:
        Path to repository root or None if not found
    """
    if start_dir is None:
        start_dir = Path.cwd()

    # Look for .folder.repo in current directory and parents
    current = start_dir
    while current != current.parent:  # Stop at filesystem root
        repo_file = current / FOLDER_FILES[FolderType.REPO]
        if repo_file.exists():
            return current
        current = current.parent

    return None
