#!/bin/bash

# Check if Modal CLI is installed
if ! command -v modal &> /dev/null
then
    echo "Modal CLI is not installed. Please install it first."
    echo "You can install it using: pip install modal"
    exit 1
fi

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Check if the deployment file exists
if [ ! -f "$SCRIPT_DIR/python/modal_deployment.py" ]; then
    echo "python/modal_deployment.py not found."
    exit 1
fi

# Change to the root autogen directory
cd "$SCRIPT_DIR"

# Find the correct pyproject.toml file
PYPROJECT_PATH=$(find . -name pyproject.toml | grep "packages/autogen-magentic-one/pyproject.toml")

if [ -z "$PYPROJECT_PATH" ]; then
    echo "Could not find pyproject.toml for autogen-magentic-one"
    exit 1
fi

# Change to the directory containing pyproject.toml
PACKAGE_DIR=$(dirname "$PYPROJECT_PATH")
echo "Changing to directory: $PACKAGE_DIR"
cd "$PACKAGE_DIR" || { echo "Failed to change directory to $PACKAGE_DIR"; exit 1; }

# Verify we're in the correct directory
if [ ! -f "pyproject.toml" ]; then
    echo "pyproject.toml not found in current directory. Current directory: $(pwd)"
    exit 1
fi

# Run uv sync
echo "Running uv sync..."
uv sync --all-extras

# Change back to the directory containing modal_deployment.py
echo "Changing back to: $SCRIPT_DIR/python"
cd "$SCRIPT_DIR/python" || { echo "Failed to change directory to $SCRIPT_DIR/python"; exit 1; }

# Verify we're in the correct directory
if [ ! -f "modal_deployment.py" ]; then
    echo "modal_deployment.py not found in current directory. Current directory: $(pwd)"
    exit 1
fi

# Deploy to Modal
echo "Deploying autogen-magentic-one to Modal..."
modal deploy modal_deployment.py

echo "Deployment completed successfully!"
