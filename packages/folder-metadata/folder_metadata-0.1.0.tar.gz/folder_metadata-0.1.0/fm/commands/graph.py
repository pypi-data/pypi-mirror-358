"""
Command to show dependency graph of projects.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set

import typer
from rich.console import Console

from fm.utils.model import FolderType
from fm.utils.io import find_all_folder_files, read_folder_metadata
from fm.utils.scanner import find_repo_root

console = Console()


def graph_cmd(
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to repository root (defaults to auto-detect)"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output results as JSON"
    ),
):
    """Show dependency graph of projects."""
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

    # Build project map and dependency graph
    projects = {}
    dependencies = {}

    for file_path in project_files:
        metadata = read_folder_metadata(file_path)
        if metadata:
            project_name = metadata.name
            projects[project_name] = {
                "path": str(file_path.parent),
                "metadata": metadata,
            }

            # Add dependencies
            if hasattr(metadata, "dependencies") and metadata.dependencies:
                dependencies[project_name] = metadata.dependencies

    # Output results
    if json_output:
        import json

        result = {
            "projects": {
                name: {"path": info["path"], "metadata": info["metadata"].dict()}
                for name, info in projects.items()
            },
            "dependencies": dependencies,
        }
        console.print(json.dumps(result, indent=2))
    else:
        # Try to use graphviz if available
        try:
            _render_graphviz(projects, dependencies)
        except ImportError:
            # Fall back to ASCII graph
            _render_ascii_graph(projects, dependencies)


def _render_graphviz(projects: Dict, dependencies: Dict):
    """Render dependency graph using graphviz."""
    import graphviz

    dot = graphviz.Digraph(comment="Project Dependencies")

    # Add nodes
    for name, info in projects.items():
        metadata = info["metadata"]
        label = f"{name}\\nv{metadata.version}\\n{metadata.language}"
        dot.node(name, label)

    # Add edges
    for project, deps in dependencies.items():
        for dep in deps:
            if dep in projects:  # Only add edge if dependency exists
                dot.edge(project, dep)

    # Render to console
    console.print("[bold]Project Dependency Graph:[/]")
    console.print(dot.source)
    console.print(
        "\n[dim]Note: Install graphviz to visualize this graph: pip install graphviz[/]"
    )


def _render_ascii_graph(projects: Dict, dependencies: Dict):
    """Render dependency graph using ASCII art."""
    console.print("[bold]Project Dependency Graph:[/]")

    # Find root projects (not depended on by others)
    all_deps = set()
    for deps in dependencies.values():
        all_deps.update(deps)

    root_projects = set(projects.keys()) - all_deps

    # If no root projects, start with all projects
    if not root_projects:
        root_projects = set(projects.keys())

    # Print graph
    visited = set()
    for root in sorted(root_projects):
        _print_project_tree(root, dependencies, projects, visited, "", True)


def _print_project_tree(
    project: str,
    dependencies: Dict[str, List[str]],
    projects: Dict,
    visited: Set[str],
    prefix: str,
    is_last: bool,
):
    """Print a project and its dependencies as a tree."""
    # Handle circular dependencies
    if project in visited:
        console.print(
            f"{prefix}{'└── ' if is_last else '├── '}[yellow]{project} (circular)[/]"
        )
        return

    # Mark as visited
    visited.add(project)

    # Get project info
    info = projects.get(project)
    if info:
        metadata = info["metadata"]
        console.print(
            f"{prefix}{'└── ' if is_last else '├── '}[bold]{project}[/] [dim]v{metadata.version}[/]"
        )
    else:
        console.print(
            f"{prefix}{'└── ' if is_last else '├── '}[red]{project} (missing)[/]"
        )
        return

    # Print dependencies
    deps = dependencies.get(project, [])
    new_prefix = prefix + ("    " if is_last else "│   ")

    for i, dep in enumerate(sorted(deps)):
        is_last_dep = i == len(deps) - 1
        _print_project_tree(
            dep, dependencies, projects, visited.copy(), new_prefix, is_last_dep
        )
