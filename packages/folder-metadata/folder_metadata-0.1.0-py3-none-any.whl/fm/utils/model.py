"""
Data models for folder metadata files.
"""

from enum import Enum
from typing import Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field


class FolderType(str, Enum):
    REPO = "repo"
    PLATFORM = "platform"
    PROJECTS = "projects"
    PROJECT = "project"


class ToolingConfig(BaseModel):
    build: Optional[str] = None
    test: Optional[str] = None
    lint: Optional[str] = None


class HooksConfig(BaseModel):
    pre_build: Optional[str] = None
    post_test: Optional[str] = None


class RepoMetadata(BaseModel):
    type: Literal["repo"] = "repo"
    name: str
    description: str


class PlatformMetadata(BaseModel):
    type: Literal["platform"] = "platform"
    name: str
    description: str


class ProjectsMetadata(BaseModel):
    type: Literal["projects"] = "projects"
    name: str
    description: str


class ProjectMetadata(BaseModel):
    type: Literal["project"] = "project"
    name: str
    language: str
    version: str
    owner: str
    team: str
    lifecycle: str
    tags: List[str] = []
    tooling: Optional[ToolingConfig] = None
    hooks: Optional[HooksConfig] = None
    dependencies: List[str] = []


# Type for any folder metadata
FolderMetadata = Union[
    RepoMetadata, PlatformMetadata, ProjectsMetadata, ProjectMetadata
]


# Mapping of folder types to their file names
FOLDER_FILES = {
    FolderType.REPO: ".folder.repo",
    FolderType.PLATFORM: ".folder.platform",
    FolderType.PROJECTS: ".folder.projects",
    FolderType.PROJECT: ".folder.project",
}

# Valid parent-child relationships
VALID_HIERARCHY = {
    FolderType.REPO: [FolderType.PLATFORM, FolderType.PROJECTS],
    FolderType.PLATFORM: [FolderType.PROJECT],
    FolderType.PROJECTS: [FolderType.PROJECT],
    FolderType.PROJECT: [],
}
