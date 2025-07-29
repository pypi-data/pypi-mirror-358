"""
Command to run defined lifecycle hooks across projects.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Optional

import typer
from rich.console import Console
from rich.panel import Panel

from fm.utils.model import FolderType
from fm.utils.io import find_all_folder_files, read_folder_metadata
from fm.utils.scanner import find_repo_root

console = Console()


def run_hooks_cmd(
    stage: str = typer.Argument(
        ..., help="Hook stage to run (pre_build, post_test, etc.)"
    ),
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to repository root (defaults to auto-detect)"
    ),
    filter_tags: Optional[List[str]] = typer.Option(
        None, "--tag", "-t", help="Only run hooks for projects with these tags"
    ),
):
    """Run defined lifecycle hooks across all applicable folders."""
    # Find repository root if path not specified
    if path is None:
        path = find_repo_root()
        if path is None:
            console.print(
                "[red]Repository root not found. Run from within a repository or specify a path.[/]"
            )
            raise typer.Exit(1)

    # Find all project folders
    project_files = find_all_folder_files(path, FolderType.PROJECT)

    # Filter projects and run hooks
    hooks_run = 0
    hooks_failed = 0

    for file_path in project_files:
        metadata = read_folder_metadata(file_path)
        if not metadata:
            continue

        # Skip if project doesn't have hooks
        if not hasattr(metadata, "hooks") or not metadata.hooks:
            continue

        # Skip if hook stage doesn't exist
        hook_script = None
        if hasattr(metadata.hooks, stage):
            hook_script = getattr(metadata.hooks, stage)

        if not hook_script:
            continue

        # Skip if tags don't match
        if filter_tags and not any(tag in metadata.tags for tag in filter_tags):
            continue

        # Run hook
        project_dir = file_path.parent
        console.print(f"[bold]Running {stage} hook for {metadata.name}...[/]")

        try:
            # Determine if script is Python or shell
            if hook_script.endswith(".py"):
                result = subprocess.run(
                    ["python", hook_script],
                    cwd=project_dir,
                    capture_output=True,
                    text=True,
                )
            else:
                result = subprocess.run(
                    ["sh", hook_script], cwd=project_dir, capture_output=True, text=True
                )

            # Check result
            if result.returncode == 0:
                console.print(
                    Panel(
                        result.stdout,
                        title=f"✅ {metadata.name} - {stage}",
                        border_style="green",
                    )
                )
                hooks_run += 1
            else:
                console.print(
                    Panel(
                        f"{result.stdout}\n\n{result.stderr}",
                        title=f"❌ {metadata.name} - {stage}",
                        border_style="red",
                    )
                )
                hooks_failed += 1
        except Exception as e:
            console.print(
                Panel(str(e), title=f"❌ {metadata.name} - {stage}", border_style="red")
            )
            hooks_failed += 1

    # Summary
    if hooks_run + hooks_failed == 0:
        console.print(f"[yellow]No {stage} hooks found.[/]")
    else:
        console.print(
            f"[bold]Summary: {hooks_run} hooks succeeded, {hooks_failed} hooks failed[/]"
        )

    # Exit with error code if any hooks failed
    if hooks_failed > 0:
        raise typer.Exit(1)
