#!/bin/bash
# Activates the project's virtual environment if pyproject.toml is found in the current or parent directories.
# Creates the venv using uv if it doesn't exist.

_activate_project() {
    local d="$PWD"
    while [ "$d" != "/" ]; do
        if [ -f "$d/pyproject.toml" ]; then
            if [ ! -d "$d/.venv" ]; then
                echo "Creating virtual environment..."
                uv sync --all-extras --no-progress || echo "Warning: Failed to create venv"
            fi
            if [ -f "$d/.venv/bin/activate" ]; then
                source "$d/.venv/bin/activate"
            fi
            break
        fi
        d=$(dirname "$d")
    done
}
_activate_project
unset -f _activate_project
