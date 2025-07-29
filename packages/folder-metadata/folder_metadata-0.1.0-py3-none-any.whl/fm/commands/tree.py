"""
Command to print logical hierarchy of the repository.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.tree import Tree as RichTree

from fm.utils.scanner import scan_repository, FolderNode, find_repo_root

console = Console()


def tree_cmd(
    path: Optional[Path] = typer.Option(
        None, "--path", "-p", help="Path to repository root (defaults to auto-detect)"
    ),
    json_output: bool = typer.Option(
        False, "--json", "-j", help="Output results as JSON"
    ),
):
    """Print logical hierarchy of the repository."""
    # Find repository root if path not specified
    if path is None:
        path = find_repo_root()
        if path is None:
            console.print(
                "[red]Repository root not found. Run from within a repository or specify a path.[/]"
            )
            raise typer.Exit(1)

    # Scan repository
    root_node, nodes = scan_repository(path)

    if not root_node:
        console.print(
            "[red]No repository structure found. Initialize with 'fm init --type repo'.[/]"
        )
        raise typer.Exit(1)

    # Output results
    if json_output:
        import json

        result = _node_to_dict(root_node)
        console.print(json.dumps(result, indent=2))
    else:
        # Create rich tree
        tree = RichTree(
            f"[bold blue]{root_node.metadata.name}[/] [dim]({root_node.path})[/]"
        )
        _build_rich_tree(root_node, tree)
        console.print(tree)


def _node_to_dict(node: FolderNode):
    """Convert a folder node to a dictionary for JSON output."""
    result = {
        "path": str(node.path),
        "type": str(node.folder_type) if node.folder_type else None,
        "name": node.metadata.name if node.metadata else None,
        "children": [],
    }

    # Add type-specific fields
    if node.metadata:
        if hasattr(node.metadata, "version"):
            result["version"] = node.metadata.version
        if hasattr(node.metadata, "language"):
            result["language"] = node.metadata.language
        if hasattr(node.metadata, "owner"):
            result["owner"] = node.metadata.owner

    # Add children
    for child in node.children:
        result["children"].append(_node_to_dict(child))

    return result


def _build_rich_tree(node: FolderNode, tree: RichTree):
    """Build a rich tree from a folder node."""
    for child in node.children:
        # Determine node style based on type
        if child.folder_type == "platform":
            style = "bold green"
        elif child.folder_type == "projects":
            style = "bold yellow"
        elif child.folder_type == "project":
            style = "bold cyan"
        else:
            style = "bold white"

        # Create node label
        if child.metadata:
            if hasattr(child.metadata, "version"):
                label = f"[{style}]{child.metadata.name}[/] [dim]v{child.metadata.version}[/] [dim]({child.path})[/]"
            else:
                label = f"[{style}]{child.metadata.name}[/] [dim]({child.path})[/]"
        else:
            label = f"[{style}]{child.path.name}[/] [dim]({child.path})[/]"

        # Add node to tree
        child_tree = tree.add(label)

        # Recursively add children
        _build_rich_tree(child, child_tree)
