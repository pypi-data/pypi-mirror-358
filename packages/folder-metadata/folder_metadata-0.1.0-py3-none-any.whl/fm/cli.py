"""
CLI interface for the fm (folder-meta) utility.
"""

import typer
from rich.console import Console
from typing import Optional

# Import version
from fm import __version__

# Import commands
from fm.commands.init import init_cmd
from fm.commands.validate import validate_cmd
from fm.commands.list import list_cmd
from fm.commands.tree import tree_cmd
from fm.commands.graph import graph_cmd
from fm.commands.bump import bump_cmd
from fm.commands.whoami import whoami_cmd
from fm.commands.hooks import run_hooks_cmd
from fm.commands.tag import tag_cmd

# Create console for rich output
console = Console()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"fm version {__version__}")
        raise typer.Exit()


# Create Typer app
app = typer.Typer(
    help="fm - Folder Metadata CLI for structured monorepos",
    add_completion=True,
)


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit",
    )
):
    """fm - Folder Metadata CLI for structured monorepos"""
    pass


# Register commands
app.command(name="init")(init_cmd)
app.command(name="validate")(validate_cmd)
app.command(name="list")(list_cmd)
app.command(name="tree")(tree_cmd)
app.command(name="graph")(graph_cmd)
app.command(name="bump")(bump_cmd)
app.command(name="whoami")(whoami_cmd)
app.command(name="run-hooks")(run_hooks_cmd)
app.command(name="tag")(tag_cmd)

if __name__ == "__main__":
    app()
