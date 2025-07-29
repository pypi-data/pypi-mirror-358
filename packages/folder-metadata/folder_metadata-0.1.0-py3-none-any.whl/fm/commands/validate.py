"""
Command to validate folder metadata structure.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from fm.utils.validator import validate_repository

console = Console()


def validate_cmd(
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to validate (defaults to current directory)"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output results as JSON"
    ),
):
    """Validate that folder metadata structure follows the rules."""
    if path is None:
        path = Path.cwd()

    # Validate repository
    errors = validate_repository(path)

    # Output results
    if json_output:
        import json

        result = {
            "valid": len(errors) == 0,
            "errors": [
                {
                    "path": str(err.path),
                    "message": err.message,
                    "severity": err.severity,
                }
                for err in errors
            ],
        }
        console.print(json.dumps(result, indent=2))
    else:
        if not errors:
            console.print("[green]Repository structure is valid![/]")
        else:
            console.print(
                f"[red]Found {len(errors)} issues in repository structure:[/]"
            )

            table = Table(show_header=True)
            table.add_column("Severity")
            table.add_column("Path")
            table.add_column("Message")

            for err in errors:
                severity_color = "red" if err.severity == "error" else "yellow"
                table.add_row(
                    f"[{severity_color}]{err.severity.upper()}[/]",
                    str(err.path),
                    err.message,
                )

            console.print(table)

    # Exit with error code if there are errors
    if errors:
        raise typer.Exit(1)
