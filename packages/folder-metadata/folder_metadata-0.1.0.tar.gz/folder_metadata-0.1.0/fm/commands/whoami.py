"""
Command to show owner/maintainer of the current folder.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel

from fm.utils.model import FolderType
from fm.utils.io import find_folder_file, read_folder_metadata

console = Console()


def whoami_cmd(
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to check (defaults to current directory)"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output results as JSON"
    ),
):
    """Show owner/maintainer of the current folder."""
    if path is None:
        path = Path.cwd()

    # Find nearest folder metadata file
    file_path, folder_type = find_folder_file(path)

    if not file_path:
        console.print(
            "[red]No folder metadata found in this directory or its parents.[/]"
        )
        raise typer.Exit(1)

    # Read metadata
    metadata = read_folder_metadata(file_path)

    if not metadata:
        console.print(f"[red]Failed to read metadata from {file_path}[/]")
        raise typer.Exit(1)

    # Output results
    if json_output:
        import json

        result = {
            "path": str(file_path.parent),
            "file": file_path.name,
            "type": metadata.type,
            "name": metadata.name,
        }

        # Add owner info if it's a project
        if hasattr(metadata, "owner"):
            result["owner"] = metadata.owner
            result["team"] = metadata.team

        console.print(json.dumps(result, indent=2))
    else:
        if hasattr(metadata, "owner"):
            console.print(
                Panel(
                    f"[bold]Project:[/] {metadata.name}\n"
                    f"[bold]Owner:[/] {metadata.owner}\n"
                    f"[bold]Team:[/] {metadata.team}\n"
                    f"[bold]Path:[/] {file_path.parent}",
                    title="Project Ownership",
                    border_style="green",
                )
            )
        else:
            console.print(
                Panel(
                    f"[bold]Name:[/] {metadata.name}\n"
                    f"[bold]Type:[/] {metadata.type}\n"
                    f"[bold]Path:[/] {file_path.parent}\n\n"
                    "[yellow]Note: This folder type doesn't have an owner field.[/]",
                    title="Folder Information",
                    border_style="blue",
                )
            )
