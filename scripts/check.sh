#!/bin/bash
set -e

# Run type checker (quiet on success)
if ! uv run pyright >/dev/null 2>&1; then
    uv run pyright
    exit 1
fi

# Run unit tests
# -x: stop on first failure
# -qq: very quiet
# --no-header: suppress header
# --disable-warnings: suppress warnings
uv run pytest -x -qq --no-header --disable-warnings
