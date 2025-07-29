"""
Command to modify tags on project folders.
"""

from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console

from fm.utils.model import FolderType
from fm.utils.io import find_folder_file, read_folder_metadata, write_folder_metadata

console = Console()


def tag_cmd(
    add: Optional[List[str]] = typer.Option(None, "--add", "-a", help="Tags to add"),
    remove: Optional[List[str]] = typer.Option(
        None, "--remove", "-r", help="Tags to remove"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to project (defaults to current directory)"
    ),
):
    """Modify tags on a project folder."""
    if path is None:
        path = Path.cwd()

    # Ensure at least one operation is specified
    if not add and not remove:
        console.print(
            "[yellow]No tags specified to add or remove. Use --add or --remove.[/]"
        )
        raise typer.Exit(1)

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
            f"[red]Found {folder_type} folder, but only project folders have tags.[/]"
        )
        raise typer.Exit(1)

    # Read metadata
    metadata = read_folder_metadata(file_path)

    if not metadata:
        console.print(f"[red]Failed to read metadata from {file_path}[/]")
        raise typer.Exit(1)

    # Get current tags
    current_tags = set(metadata.tags)
    original_tags = set(current_tags)

    # Add tags
    if add:
        for tag in add:
            current_tags.add(tag)

    # Remove tags
    if remove:
        for tag in remove:
            if tag in current_tags:
                current_tags.remove(tag)

    # Update metadata if tags changed
    if current_tags != original_tags:
        metadata.tags = sorted(list(current_tags))

        # Write updated metadata
        if write_folder_metadata(file_path, metadata):
            console.print(f"[green]Updated tags: {', '.join(metadata.tags)}[/]")
        else:
            console.print(f"[red]Failed to write updated metadata to {file_path}[/]")
            raise typer.Exit(1)
    else:
        console.print("[yellow]No changes to tags.[/]")
