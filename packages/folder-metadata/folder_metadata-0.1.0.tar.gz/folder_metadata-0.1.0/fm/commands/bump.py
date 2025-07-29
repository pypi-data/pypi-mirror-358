"""
Command to bump version in a project folder.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from semver import VersionInfo

from fm.utils.model import FolderType
from fm.utils.io import find_folder_file, read_folder_metadata, write_folder_metadata

console = Console()


def bump_cmd(
    bump_type: str = typer.Argument(
        ..., help="Type of version bump (major, minor, patch)"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to project (defaults to current directory)"
    ),
):
    """Increment version of a project folder."""
    if path is None:
        path = Path.cwd()

    # Find nearest folder metadata file
    file_path, folder_type = find_folder_file(path)

    if not file_path:
        console.print(
            "[red]No folder metadata found in this directory or its parents.[/]"
        )
        raise typer.Exit(1)

    # Check if it's a project folder
    if folder_type != FolderType.PROJECT:
        console.print(
            f"[red]Found {folder_type} folder, but only project folders have versions to bump.[/]"
        )
        raise typer.Exit(1)

    # Read metadata
    metadata = read_folder_metadata(file_path)

    if not metadata:
        console.print(f"[red]Failed to read metadata from {file_path}[/]")
        raise typer.Exit(1)

    # Parse current version
    try:
        current_version = VersionInfo.parse(metadata.version)
    except ValueError:
        console.print(f"[red]Invalid version format: {metadata.version}[/]")
        console.print("[yellow]Version should follow semver format (e.g., 1.2.3)[/]")
        raise typer.Exit(1)

    # Bump version
    if bump_type == "major":
        new_version = current_version.bump_major()
    elif bump_type == "minor":
        new_version = current_version.bump_minor()
    elif bump_type == "patch":
        new_version = current_version.bump_patch()
    else:
        console.print(f"[red]Invalid bump type: {bump_type}[/]")
        console.print("[yellow]Valid types: major, minor, patch[/]")
        raise typer.Exit(1)

    # Update metadata
    metadata.version = str(new_version)

    # Write updated metadata
    if write_folder_metadata(file_path, metadata):
        console.print(
            f"[green]Bumped version from {current_version} to {new_version}[/]"
        )
    else:
        console.print(f"[red]Failed to write updated metadata to {file_path}[/]")
        raise typer.Exit(1)
