# Folder Metadata (fm)

A powerful CLI tool for managing structured metadata in monorepos and multi-project repositories. `fm` helps you organize, validate, and maintain hierarchical folder structures with type-safe metadata files.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

`fm` (Folder Metadata) is designed for teams working with complex repository structures containing multiple projects, platforms, and organizational units. It provides a systematic way to:

- **Define folder types** with structured metadata
- **Enforce hierarchical relationships** between different folder types
- **Validate repository structure** automatically
- **Query and visualize** project organization
- **Automate workflows** with hooks and tooling configuration

## Features

- 🏗️ **Structured Metadata**: Type-safe folder metadata with validation
- 🌳 **Hierarchical Organization**: Enforce parent-child relationships between folder types
- 🔍 **Discovery & Search**: Find and list folders by type across your repository
- 📊 **Visualization**: Generate tree and graph views of your repository structure
- ✅ **Validation**: Ensure repository structure follows defined rules
- 🚀 **Automation**: Built-in hooks for build, test, and deployment workflows
- 🏷️ **Tagging**: Organize projects with custom tags
- 📦 **Version Management**: Semantic versioning support for projects

## Installation

### From PyPI (Recommended)

```bash
pip install folder-metadata
```

### From Source

```bash
git clone https://github.com/yourusername/folder-metadata.git
cd folder-metadata
pip install -e .
```

### Dependencies

The tool requires the following Python packages:

- `typer` - CLI framework
- `rich` - Rich text and beautiful formatting
- `pydantic` - Data validation and settings management
- `semver` - Semantic versioning

## Quick Start

### 1. Initialize Repository Root

```bash
# Navigate to your repository root
cd /path/to/your/repo

# Initialize as a repository
fm init --type repo
```

### 2. Create Platform/Projects Structure

```bash
# Create a platform folder
mkdir backend
cd backend
fm init --type platform

# Create a projects collection
mkdir ../apps
cd ../apps
fm init --type projects
```

### 3. Add Individual Projects

```bash
# Create and initialize a project
mkdir user-service
cd user-service
fm init --type project
```

### 4. Validate Your Structure

```bash
# Validate from repository root
fm validate

# View the complete structure
fm tree
```

## Folder Types

`fm` supports four hierarchical folder types:

### Repository (`.folder.repo`)

The root level of your repository.

```yaml
type: repo
name: "my-awesome-repo"
description: "A comprehensive multi-service application"
```

### Platform (`.folder.platform`)

Groups related projects by technology stack or domain.

```yaml
type: platform
name: "backend-services"
description: "Node.js microservices platform"
```

### Projects Collection (`.folder.projects`)

Organizes multiple related projects.

```yaml
type: projects
name: "mobile-apps"
description: "iOS and Android applications"
```

### Project (`.folder.project`)

Individual deployable units with detailed metadata.

```yaml
type: project
name: "user-service"
language: "typescript"
version: "1.2.3"
owner: "backend-team"
team: "platform"
lifecycle: "production"
tags: ["api", "microservice", "auth"]
tooling:
  build: "npm run build"
  test: "npm test"
  lint: "npm run lint"
hooks:
  pre_build: "npm install"
  post_test: "npm run coverage"
dependencies: ["auth-service", "database"]
```

## Hierarchy Rules

The folder types must follow this hierarchical structure:

```text
Repository Root (.folder.repo)
├── Platform (.folder.platform)
│   └── Project (.folder.project)
└── Projects (.folder.projects)
    └── Project (.folder.project)
```

## Commands

### `fm init`

Initialize a folder with metadata.

```bash
# Interactive initialization
fm init

# Specify type directly
fm init --type project

# Force overwrite existing metadata
fm init --type project --force
```

### `fm validate`

Validate repository structure and metadata.

```bash
# Validate current directory
fm validate

# Validate specific path
fm validate --path /path/to/repo

# JSON output
fm validate --json
```

### `fm list`

List folders of a specific type.

```bash
# List all projects
fm list --type project

# List platforms with JSON output
fm list --type platform --json

# Search from specific path
fm list --type project --path /custom/path
```

### `fm tree`

Display repository structure as a tree.

```bash
# Show tree from auto-detected root
fm tree

# Show tree from specific path
fm tree --path /path/to/repo

# JSON output
fm tree --json
```

### `fm graph`

Generate dependency graphs.

```bash
# Show project dependencies
fm graph

# Output in different formats
fm graph --format dot
fm graph --format json
```

### `fm bump`

Increment project versions (semantic versioning).

```bash
# Bump patch version (1.0.0 → 1.0.1)
fm bump patch

# Bump minor version (1.0.1 → 1.1.0)
fm bump minor

# Bump major version (1.1.0 → 2.0.0)
fm bump major

# Bump specific project
fm bump patch --path /path/to/project
```

### `fm whoami`

Display current folder information.

```bash
# Show current folder metadata
fm whoami
```

### `fm tag`

Manage project tags.

```bash
# Add tags to current project
fm tag add api microservice

# Remove tags
fm tag remove deprecated

# List all tags in repository
fm tag list
```

### `fm run-hooks`

Execute configured hooks.

```bash
# Run pre-build hooks
fm run-hooks pre_build

# Run post-test hooks
fm run-hooks post_test
```

## Example Repository Structure

```text
my-monorepo/                      # .folder.repo
├── platforms/                    
│   ├── backend/                  # .folder.platform
│   │   ├── user-service/         # .folder.project (Node.js API)
│   │   ├── auth-service/         # .folder.project (Authentication)
│   │   └── payment-service/      # .folder.project (Payment processing)
│   └── frontend/                 # .folder.platform
│       ├── web-app/              # .folder.project (React SPA)
│       └── admin-panel/          # .folder.project (Admin interface)
├── mobile/                       # .folder.projects
│   ├── ios-app/                  # .folder.project (Swift/iOS)
│   └── android-app/              # .folder.project (Kotlin/Android)
└── shared/                       # .folder.projects
    ├── ui-components/            # .folder.project (Shared UI library)
    └── utils/                    # .folder.project (Common utilities)
```

## Configuration

### Project Tooling

Configure build, test, and lint commands:

```yaml
tooling:
  build: "npm run build"
  test: "npm test -- --coverage"
  lint: "eslint src/ --fix"
```

### Hooks

Set up automation hooks:

```yaml
hooks:
  pre_build: "npm install && npm run generate"
  post_test: "npm run coverage-report"
```

### Project Dependencies

Track project dependencies:

```yaml
dependencies:
  - "auth-service"
  - "shared/utils"
  - "database"
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Development

### Setting up Development Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/folder-metadata.git
cd folder-metadata

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=fm

# Run specific test file
pytest tests/test_commands.py
```

### Code Quality

```bash
# Format code
black fm/

# Lint code
flake8 fm/

# Type checking
mypy fm/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Peter Corcoran

## Roadmap

- [ ] **Web Dashboard**: Browser-based repository visualization
- [ ] **CI/CD Integration**: GitHub Actions and GitLab CI templates  
- [ ] **Import/Export**: Support for other metadata formats
- [ ] **Plugins**: Extensible command system
- [ ] **Templates**: Project scaffolding from templates
- [ ] **Metrics**: Repository health and complexity metrics
