set shell := ["bash", "-c"]

export UV_FROZEN := "true"

[private]
default:
  just --list

# Update uv.lock dependencies
[group("dev")]
lock:
    uv lock --upgrade --no-cache

# Run all quality checks
[group("dev")]
check: format lint test

# Lint the codebase using ruff
[group("dev")]
lint: && format
    # Lint the code
    uv run ruff check
    # Run static checks
    uv run pyright src
    # Check for dead code
    uv run vulture src --min-confidence=80 --ignore-names="parameters"

# Format the codebase using ruff
[group("dev")]
format:
    # Fix generic linting issues
    uv run ruff check --fix-only
    # Fix import-related issues (including ordering)
    uv run ruff check --select=I --fix-only
    # Format the code
    uv run ruff format

# Run tests
[group("dev")]
test:
    uv run pytest

# Build the project
[group("build")]
build:
    uv build

# Remove build artifacts, caches, and temporary files
[group("build")]
clean:
    # Remove __pycache__ directories
    find . -type d -name "__pycache__" -exec rm -r {} + || true
    # Remove .pytest_cache directory
    rm -rf .pytest_cache
    # Remove build/dist/egg-info directories
    rm -rf build dist *.egg-info
    # Remove coverage reports
    rm -f .coverage coverage.xml

# Create a GitHub release (which will trigger a PyPi release)
[group("release")]
release:
    #!/usr/bin/env bash
    latest_release="$(gh release list --limit=1 --order=desc --json=tagName | jq -r '.[].tagName')"
    echo "Latest release on GitHub is ${latest_release}"
    pyproject_release="$(yq -oy .project.version pyproject.toml)"
    echo "Current version in pyproject.toml is v${pyproject_release}"
    echo
    read -p "Proceed releasing v${pyproject_release}? (y/n): " answer
    if [[ ! "$answer" == [Yy] ]] ; then
        echo "Cancelled."
        exit 1
    fi
    gh release create "v${pyproject_release}" --generate-notes --notes-start-tag="${latest_release}"

# Run the app with Textual
[group("dev")]
run:
	uv run textual run src/hledger_tui/app.py --dev
