"""Test the CLI interface."""

import pytest
from typer.testing import CliRunner
from fm.cli import app
from pathlib import Path

runner = CliRunner()


def test_cli_help():
    """Test that the CLI shows help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "fm - Folder Metadata CLI" in result.stdout


def test_init_command_help():
    """Test init command help."""
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "Initialize a folder metadata file" in result.stdout


def test_validate_command_help():
    """Test validate command help."""
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
    assert "Validate that folder metadata structure" in result.stdout


def test_list_command_help():
    """Test list command help."""
    result = runner.invoke(app, ["list", "--help"])
    assert result.exit_code == 0
    assert "List all folders" in result.stdout


def test_tree_command_help():
    """Test tree command help."""
    result = runner.invoke(app, ["tree", "--help"])
    assert result.exit_code == 0
    assert "Print logical hierarchy" in result.stdout
