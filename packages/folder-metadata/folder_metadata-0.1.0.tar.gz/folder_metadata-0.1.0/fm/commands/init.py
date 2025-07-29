"""
Command to initialize a folder metadata file.
"""

import os
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm

from fm.utils.model import (
    FolderType,
    FOLDER_FILES,
    RepoMetadata,
    PlatformMetadata,
    ProjectsMetadata,
    ProjectMetadata,
    ToolingConfig,
    HooksConfig,
)
from fm.utils.io import find_folder_file, write_folder_metadata

console = Console()


def init_cmd(
    folder_type: Optional[str] = typer.Option(
        None,
        "--type",
        "-t",
        help="Type of folder to initialize (repo, platform, projects, project)",
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Overwrite existing folder metadata file"
    ),
):
    """Initialize a folder metadata file in the current directory."""
    current_dir = Path.cwd()

    # Check if a folder metadata file already exists
    existing_file, existing_type = find_folder_file(current_dir)
    if existing_file and existing_file.parent == current_dir and not force:
        console.print(
            f"[yellow]A folder metadata file already exists: {existing_file.name}[/]"
        )
        if not Confirm.ask("Do you want to overwrite it?"):
            raise typer.Abort()

    # Determine folder type
    if not folder_type:
        folder_type = Prompt.ask(
            "Select folder type",
            choices=["repo", "platform", "projects", "project"],
            default="project",
        )

    # Create metadata based on folder type
    if folder_type == "repo":
        metadata = _create_repo_metadata()
        file_path = current_dir / FOLDER_FILES[FolderType.REPO]
    elif folder_type == "platform":
        metadata = _create_platform_metadata()
        file_path = current_dir / FOLDER_FILES[FolderType.PLATFORM]
    elif folder_type == "projects":
        metadata = _create_projects_metadata()
        file_path = current_dir / FOLDER_FILES[FolderType.PROJECTS]
    elif folder_type == "project":
        metadata = _create_project_metadata()
        file_path = current_dir / FOLDER_FILES[FolderType.PROJECT]
    else:
        console.print(f"[red]Invalid folder type: {folder_type}[/]")
        raise typer.Abort()

    # Write metadata to file
    if write_folder_metadata(file_path, metadata):
        console.print(f"[green]Created {file_path.name} successfully[/]")
    else:
        console.print(f"[red]Failed to create {file_path.name}[/]")
        raise typer.Exit(1)


def _create_repo_metadata() -> RepoMetadata:
    """Create repo metadata interactively."""
    name = Prompt.ask("Repository name", default=Path.cwd().name)
    description = Prompt.ask("Repository description", default="Top-level monorepo")

    return RepoMetadata(type="repo", name=name, description=description)


def _create_platform_metadata() -> PlatformMetadata:
    """Create platform metadata interactively."""
    name = Prompt.ask("Platform name", default=Path.cwd().name)
    description = Prompt.ask("Platform description", default="Shared services platform")

    return PlatformMetadata(type="platform", name=name, description=description)


def _create_projects_metadata() -> ProjectsMetadata:
    """Create projects metadata interactively."""
    name = Prompt.ask("Projects group name", default=Path.cwd().name)
    description = Prompt.ask(
        "Projects group description", default="Collection of related projects"
    )

    return ProjectsMetadata(type="projects", name=name, description=description)


def _create_project_metadata() -> ProjectMetadata:
    """Create project metadata interactively."""
    name = Prompt.ask("Project name", default=Path.cwd().name)
    language = Prompt.ask("Programming language", default="python")
    version = Prompt.ask("Version", default="0.1.0")
    owner = Prompt.ask("Owner", default=os.environ.get("USER", "unknown"))
    team = Prompt.ask("Team", default="engineering")
    lifecycle = Prompt.ask(
        "Lifecycle stage",
        choices=["planning", "development", "active", "maintenance", "deprecated"],
        default="development",
    )

    tags_input = Prompt.ask("Tags (comma-separated)", default="")
    tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

    # Tooling
    use_tooling = Confirm.ask("Configure tooling?", default=True)
    tooling = None
    if use_tooling:
        build = Prompt.ask("Build tool", default="poetry")
        test = Prompt.ask("Test tool", default="pytest")
        lint = Prompt.ask("Lint tool", default="black")
        tooling = ToolingConfig(build=build, test=test, lint=lint)

    # Hooks
    use_hooks = Confirm.ask("Configure hooks?", default=False)
    hooks = None
    if use_hooks:
        pre_build = Prompt.ask("Pre-build hook", default="")
        post_test = Prompt.ask("Post-test hook", default="")
        hooks = HooksConfig(
            pre_build=pre_build if pre_build else None,
            post_test=post_test if post_test else None,
        )

    # Dependencies
    deps_input = Prompt.ask("Dependencies (comma-separated)", default="")
    dependencies = [dep.strip() for dep in deps_input.split(",") if dep.strip()]

    return ProjectMetadata(
        type="project",
        name=name,
        language=language,
        version=version,
        owner=owner,
        team=team,
        lifecycle=lifecycle,
        tags=tags,
        tooling=tooling,
        hooks=hooks,
        dependencies=dependencies,
    )
