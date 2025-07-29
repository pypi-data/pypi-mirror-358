"""
Command to list folders of a specific type.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from fm.utils.model import FolderType
from fm.utils.io import find_all_folder_files, read_folder_metadata
from fm.utils.scanner import find_repo_root

console = Console()


def list_cmd(
    folder_type: str = typer.Option(
        ...,
        "--type",
        "-t",
        help="Type of folders to list (repo, platform, projects, project)",
    ),
    path: Optional[Path] = typer.Option(
        None,
        "--path",
        "-p",
        help="Path to start searching from (defaults to repository root)",
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output results as JSON"
    ),
):
    """List all folders of the specified type."""
    # Validate folder type
    try:
        folder_type_enum = FolderType(folder_type)
    except ValueError:
        console.print(f"[red]Invalid folder type: {folder_type}[/]")
        console.print("[yellow]Valid types: repo, platform, projects, project[/]")
        raise typer.Exit(1)

    # Find repository root if path not specified
    if path is None:
        path = find_repo_root()
        if path is None:
            console.print(
                "[red]Repository root not found. Run from within a repository or specify a path.[/]"
            )
            raise typer.Exit(1)

    # Find all folder files of the specified type
    files = find_all_folder_files(path, folder_type_enum)

    # Read metadata from each file
    folders = []
    for file_path in files:
        metadata = read_folder_metadata(file_path)
        if metadata:
            folders.append(
                {
                    "path": str(file_path.parent),
                    "name": metadata.name,
                    "metadata": metadata,
                }
            )

    # Output results
    if json_output:
        import json

        result = {
            "count": len(folders),
            "folders": [
                {
                    "path": folder["path"],
                    "name": folder["name"],
                    "metadata": folder["metadata"].dict(),
                }
                for folder in folders
            ],
        }
        console.print(json.dumps(result, indent=2))
    else:
        if not folders:
            console.print(f"[yellow]No folders of type '{folder_type}' found.[/]")
        else:
            console.print(
                f"[green]Found {len(folders)} folders of type '{folder_type}':[/]"
            )

            table = Table(show_header=True)
            table.add_column("Name")
            table.add_column("Path")

            # Add type-specific columns
            if folder_type == "project":
                table.add_column("Language")
                table.add_column("Version")
                table.add_column("Owner")

            for folder in folders:
                metadata = folder["metadata"]
                if folder_type == "project":
                    table.add_row(
                        metadata.name,
                        folder["path"],
                        metadata.language,
                        metadata.version,
                        metadata.owner,
                    )
                else:
                    table.add_row(metadata.name, folder["path"])

            console.print(table)
