"""Test the data models."""

import pytest
from pydantic import ValidationError
from fm.utils.model import (
    RepoMetadata,
    PlatformMetadata,
    ProjectsMetadata,
    ProjectMetadata,
    FolderType,
    FOLDER_FILES,
    VALID_HIERARCHY,
)


def test_repo_metadata():
    """Test RepoMetadata model."""
    repo = RepoMetadata(name="test-repo", description="Test repository")
    assert repo.type == "repo"
    assert repo.name == "test-repo"
    assert repo.description == "Test repository"


def test_platform_metadata():
    """Test PlatformMetadata model."""
    platform = PlatformMetadata(name="backend", description="Backend platform")
    assert platform.type == "platform"
    assert platform.name == "backend"


def test_project_metadata():
    """Test ProjectMetadata model."""
    project = ProjectMetadata(
        name="api-service",
        language="python",
        version="1.0.0",
        owner="team",
        team="backend",
        lifecycle="production",
    )
    assert project.type == "project"
    assert project.name == "api-service"
    assert project.language == "python"
    assert project.version == "1.0.0"
    assert project.tags == []  # default empty list


def test_project_metadata_with_tags():
    """Test ProjectMetadata with tags."""
    project = ProjectMetadata(
        name="api-service",
        language="python",
        version="1.0.0",
        owner="team",
        team="backend",
        lifecycle="production",
        tags=["api", "microservice"],
    )
    assert project.tags == ["api", "microservice"]


def test_folder_types():
    """Test FolderType enum."""
    assert FolderType.REPO == "repo"
    assert FolderType.PLATFORM == "platform"
    assert FolderType.PROJECTS == "projects"
    assert FolderType.PROJECT == "project"


def test_folder_files_mapping():
    """Test FOLDER_FILES mapping."""
    assert FOLDER_FILES[FolderType.REPO] == ".folder.repo"
    assert FOLDER_FILES[FolderType.PLATFORM] == ".folder.platform"
    assert FOLDER_FILES[FolderType.PROJECTS] == ".folder.projects"
    assert FOLDER_FILES[FolderType.PROJECT] == ".folder.project"


def test_valid_hierarchy():
    """Test VALID_HIERARCHY mapping."""
    assert FolderType.PLATFORM in VALID_HIERARCHY[FolderType.REPO]
    assert FolderType.PROJECTS in VALID_HIERARCHY[FolderType.REPO]
    assert FolderType.PROJECT in VALID_HIERARCHY[FolderType.PLATFORM]
    assert FolderType.PROJECT in VALID_HIERARCHY[FolderType.PROJECTS]
    assert VALID_HIERARCHY[FolderType.PROJECT] == []
