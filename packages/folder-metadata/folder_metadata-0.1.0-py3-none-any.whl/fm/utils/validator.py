"""
Validator for folder metadata structure.
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from fm.utils.model import FolderType, VALID_HIERARCHY
from fm.utils.scanner import FolderNode, scan_repository


class ValidationError:
    """Represents a validation error in the repository structure."""

    def __init__(self, path: Path, message: str, severity: str = "error"):
        self.path = path
        self.message = message
        self.severity = severity  # "error" or "warning"

    def __repr__(self):
        return f"{self.severity.upper()}: {self.path} - {self.message}"


def validate_repository(root_dir: Path = None) -> List[ValidationError]:
    """
    Validate the repository structure and return any errors.

    Args:
        root_dir: Root directory to validate (defaults to current directory)

    Returns:
        List of ValidationError objects
    """
    if root_dir is None:
        root_dir = Path.cwd()

    errors = []

    # Scan repository
    root_node, nodes = scan_repository(root_dir)

    # Check if repo root exists
    if root_node is None or root_node.folder_type != FolderType.REPO:
        errors.append(
            ValidationError(
                root_dir, "Repository root (.folder.repo) not found", "error"
            )
        )
        return errors  # Can't validate further without a root

    # Check for multiple .folder.* files in the same directory
    dir_counts = {}
    for node in nodes.values():
        if node.path not in dir_counts:
            dir_counts[node.path] = 0
        dir_counts[node.path] += 1

    for path, count in dir_counts.items():
        if count > 1:
            errors.append(
                ValidationError(
                    path,
                    f"Multiple .folder.* files found in the same directory ({count})",
                    "error",
                )
            )

    # Validate parent-child relationships
    for node in nodes.values():
        if node.parent:
            parent_type = node.parent.folder_type
            child_type = node.folder_type

            if (
                parent_type in VALID_HIERARCHY
                and child_type not in VALID_HIERARCHY[parent_type]
            ):
                errors.append(
                    ValidationError(
                        node.path,
                        f"Invalid parent-child relationship: {parent_type} -> {child_type}",
                        "error",
                    )
                )

    # Validate there's only one repo root
    repo_roots = [n for n in nodes.values() if n.folder_type == FolderType.REPO]
    if len(repo_roots) > 1:
        for repo_node in repo_roots[1:]:
            errors.append(
                ValidationError(
                    repo_node.path,
                    "Multiple repository roots (.folder.repo) found",
                    "error",
                )
            )

    return errors
