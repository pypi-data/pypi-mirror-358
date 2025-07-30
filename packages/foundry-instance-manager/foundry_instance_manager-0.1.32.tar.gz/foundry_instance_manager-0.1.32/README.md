# Foundry Instance Manager

## THIS PROJECT IS IN PROGRESS AND NOT READY FOR USE

A CLI tool for managing multiple Docker containers that share the same image but have individual data directories and a shared data directory.

## Features

- Create and manage multiple Docker containers from the same image
- Each container has its own isolated data directory
- Shared data directory accessible by all containers
- Easy-to-use CLI interface
- Container status monitoring
- **Automated changelog generation**
- **Automated version bumping and release workflow**
- **Security checks (Bandit, Safety)**

## Installation

1. Clone this repository
2. Install [Poetry](https://python-poetry.org/docs/#installation)
3. Install dependencies:
```bash
poetry install
```

## Usage

```bash
# Create a new container
poetry run fim create --name my-container --image my-image

# List all containers
poetry run fim list

# Start a container
poetry run fim start --name my-container

# Stop a container
poetry run fim stop --name my-container

# Remove a container
poetry run fim remove --name my-container
```

## Configuration

The tool uses the following directory structure:
- `./data/shared/` - Shared data directory accessible by all containers
- `./data/containers/<container-name>/` - Individual container data directories

## Requirements

- Python 3.9+
- Docker installed and running
- Poetry

## CI/CD Pipeline (GitHub Actions)

This project uses a robust CI/CD pipeline with the following stages:

- **Quality Checks**: Linting (flake8, black, isort), type checking (mypy), and unit tests with coverage (pytest, pytest-cov). Coverage is uploaded to Codecov.
- **Security**: Bandit for static security analysis and Safety for dependency vulnerability checks.
- **Version Management**: Automated version bumping and changelog generation on every push to `main`.
- **Release**: Builds the package, creates a GitHub release, and publishes to PyPI when a new tag is created.

### How it works
- On every push or pull request to `main`, the pipeline runs quality and security checks.
- On pushes to `main`, if all checks pass, the version is bumped, a changelog is generated, and a new tag is created.
- When a tag is pushed, a release is created and the package is published to PyPI.

## Changelog Generation

Changelog is automatically generated using the `changelog` tool. To manually generate or update the changelog:
```bash
poetry run changelog generate-md CHANGELOG.md
```

## Security

- Run Bandit:
  ```bash
  poetry run bandit -r foundry_instance_manager
  ```
- Run Safety:
  ```bash
  poetry run safety check
  ```
